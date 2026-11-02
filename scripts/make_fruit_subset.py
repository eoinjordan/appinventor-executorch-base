"""Pick the pinned 1,200-photo subset from the Fruit Recognition dataset and write models/fruit_dataset.zip.

Maintainers run this once against the extracted Zenodo archive. The result is checked in,
so training and export never need the 8.5 GB download. The selection is deterministic:
byte-identical repeats are dropped, files are sorted by archive path, shuffled with a fixed
seed, and the first 400 per class
are taken, 300 for Training and 100 for Test. Re-running against the same archive yields
the same zip and manifest.
"""
import argparse
import hashlib
import io
import json
import random
import zipfile
from pathlib import Path

from PIL import Image

SOURCE = dict(
    dataset='Fruit Recognition dataset',
    authors='Israr Hussain, Qianhua He, Zhuliang Chen, Wei Xie (South China University of Technology)',
    doi='10.5281/zenodo.1310165',
    url='https://zenodo.org/records/1310165',
    archive='Fruit -Database.rar',
    archive_md5='d43d94ae62097e0e5bc63b11cedf387b',
    license='CC BY 4.0',
    license_url='https://creativecommons.org/licenses/by/4.0/',
)
# App label -> class folder inside the archive. Apple has variety subfolders A-F; the
# 'Total Number of Apples' folder repeats them and is skipped.
CLASSES = [('apple', 'Apple'), ('banana', 'Banana'), ('orange', 'Orange')]
PER_CLASS_TRAIN, PER_CLASS_TEST, SEED = 300, 100, 42
MAX_SIDE = 128  # Originals are about 320 x 258; the model uses 32 x 32, so this keeps the zip small.

ATTRIBUTION = """# Dataset attribution

Fruit Recognition dataset. Israr Hussain, Qianhua He, Zhuliang Chen and Wei Xie,
South China University of Technology, 2018. https://doi.org/10.5281/zenodo.1310165

Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/

This zip holds a subset of 1,200 photos (400 per class for apple, banana and orange),
selected deterministically by scripts/make_fruit_subset.py, converted to RGB JPEG and
resized so the longer side is at most 128 pixels. Original paths inside the Zenodo
archive and the content hashes of these resized copies are listed in manifest.json.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive_root', type=Path, help='Folder the Zenodo RAR was extracted into')
    parser.add_argument('--output', type=Path, default=Path('models'))
    args = parser.parse_args()

    rng = random.Random(SEED)
    records, blobs = [], {}
    for label, folder in CLASSES:
        files = sorted(p for p in (args.archive_root / folder).rglob('*')
                       if p.suffix.lower() in ('.png', '.jpg', '.jpeg') and 'Total Number' not in p.parts[-2])
        # The archive repeats some photos under different names; keep the first of each.
        seen, unique = set(), []
        for p in files:
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            if digest not in seen:
                seen.add(digest)
                unique.append(p)
        print(f'{folder}: {len(files)} files, {len(unique)} unique')
        files = unique
        assert len(files) >= PER_CLASS_TRAIN + PER_CLASS_TEST, f'{folder}: {len(files)} files'
        chosen = files[:]
        rng.shuffle(chosen)
        chosen = chosen[:PER_CLASS_TRAIN + PER_CLASS_TEST]
        for i, source in enumerate(chosen):
            split = 'Training' if i < PER_CLASS_TRAIN else 'Test'
            with Image.open(source) as image:
                image = image.convert('RGB')
                image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                image.save(buffer, 'JPEG', quality=90, optimize=True)
            data = buffer.getvalue()
            archive_path = source.relative_to(args.archive_root).as_posix()
            # Apple varieties reuse file names, so the variety folder becomes part of the name.
            variety = source.parent.name.replace(' ', '-').lower()
            stem = source.stem.replace(' ', '-')
            path = f'{split}/{label}/{stem}.jpg' if source.parent.name == folder else f'{split}/{label}/{variety}-{stem}.jpg'
            assert path not in blobs, path
            blobs[path] = data
            records.append(dict(split=split, label=label, path=path, archive_path=archive_path,
                                url=SOURCE['url'], sha256=hashlib.sha256(data).hexdigest()))
    manifest = dict(**SOURCE, revision=SOURCE['doi'], seed=SEED, max_side=MAX_SIDE,
                    transformations='RGB conversion; resized so the longer side is at most 128 px; JPEG quality 90.',
                    images=sorted(records, key=lambda r: r['path']))
    args.output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output / 'fruit_dataset.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for record in manifest['images']:
            info = zipfile.ZipInfo(record['path'], date_time=(2018, 7, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, blobs[record['path']])
        z.writestr(zipfile.ZipInfo('manifest.json', date_time=(2018, 7, 12, 0, 0, 0)), json.dumps(manifest, indent=2))
        z.writestr(zipfile.ZipInfo('ATTRIBUTION.md', date_time=(2018, 7, 12, 0, 0, 0)), ATTRIBUTION)
    (args.output / 'fruit_dataset_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    train = sum(r['split'] == 'Training' for r in manifest['images'])
    print(f'Wrote {args.output / "fruit_dataset.zip"}: {train} training + {len(manifest["images"]) - train} test photos')


if __name__ == '__main__':
    main()
