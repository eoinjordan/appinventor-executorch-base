"""Render a labelled contact sheet from actual, hash-verified training photos."""
from pathlib import Path
import hashlib
import io
import json
import zipfile

from PIL import Image, ImageDraw
from make_training_gifs import font

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT/'models/fruit_dataset_manifest.json').read_text(encoding='utf-8'))
    canvas = Image.new('RGB', (1000, 960), '#f3f6f2')
    draw = ImageDraw.Draw(canvas)
    draw.text((38, 24), 'Meet the fruit dataset', font=font(32), fill='#18352b')
    draw.text((38, 70), 'Actual training photos from the pinned Fruit Recognition subset', font=font(18), fill='#586a62')
    counts = {(r['split'], r['label']): 0 for r in manifest['images']}
    for r in manifest['images']:
        counts[(r['split'], r['label'])] += 1
    selected = []
    with zipfile.ZipFile(ROOT/'models/fruit_dataset.zip') as archive:
        for row, label in enumerate(['apple', 'banana', 'orange']):
            records = [r for r in manifest['images'] if r['split']=='Training' and r['label']==label]
            y = 120+row*250
            draw.rounded_rectangle((24, y, 976, y+234), radius=16, fill='white')
            draw.text((42, y+28), label.title(), font=font(26), fill='#246747')
            draw.text((42, y+76), f"{counts[('Training', label)]} training", font=font(16), fill='#586a62')
            draw.text((42, y+102), f"{counts[('Test', label)]} test", font=font(16), fill='#586a62')
            for column, index in enumerate([0, len(records)//2, len(records)-1]):
                record = records[index]
                data = archive.read(record['path'])
                assert hashlib.sha256(data).hexdigest()==record['sha256']
                with Image.open(io.BytesIO(data)) as source:
                    image = source.convert('RGB').resize((200, 200), Image.Resampling.BILINEAR)
                canvas.paste(image, (270+column*226, y+17))
                selected.append(record)
    total_train = sum(v for (s, _), v in counts.items() if s == 'Training')
    total_test = sum(v for (s, _), v in counts.items() if s == 'Test')
    draw.text((38, 886), f'{total_train} training + {total_test} separate test photos | 3 classes | varied lab lighting',
              font=font(18), fill='#18352b')
    draw.text((38, 922), 'Photos: Hussain, He, Chen, Xie / Fruit Recognition dataset | CC BY 4.0 | See linked attribution',
              font=font(16), fill='#586a62')
    output = ROOT/'docs/images'
    output.mkdir(parents=True, exist_ok=True)
    canvas.save(output/'fruit-dataset.png', optimize=True)
    (output/'fruit-dataset-sources.json').write_text(json.dumps({
        'dataset': manifest['dataset'], 'doi': manifest['doi'], 'license': manifest['license'],
        'transformations': 'Selected training photographs resized and arranged with labels.',
        'images': selected,
    }, indent=2), encoding='utf-8')
    print('Saved dataset preview from nine verified training images')


if __name__ == '__main__':
    main()
