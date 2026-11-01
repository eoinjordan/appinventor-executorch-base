"""Run the tutorial commands and render their actual output as animated transcripts.

Requires the optional training/export environment and Pillow. No device or UI
recording is involved. Raw transcripts are saved beside the GIFs for accessibility.
"""
from pathlib import Path
import json
import os
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'docs/tutorials'


def font(size):
    for name in ['C:/Windows/Fonts/consola.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def animate(title, command, transcript, destination):
    lines = []
    for line in ('$ '+command+'\n\n'+transcript).splitlines():
        lines.extend(textwrap.wrap(line, width=101, replace_whitespace=False) or [''])
    frames = []
    durations = []
    for count in range(1, len(lines)+1):
        frame = Image.new('RGB', (1160, 540), '#101b26')
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((16, 16, 1144, 70), radius=12, fill='#203447')
        draw.text((34, 30), title, font=font(23), fill='#f0f6fc')
        for index, line in enumerate(lines[max(0, count-17):count]):
            colour = '#8ee3ad' if line.startswith('$') else '#e4edf5'
            draw.text((34, 90+index*23), line, font=font(18), fill=colour)
        draw.text((34, 507), 'Actual command output replay | See the guide for copyable commands',
                  font=font(15), fill='#9fb2c5')
        frames.append(frame)
        durations.append(650)
    durations[-1] = 6000
    frames[0].save(destination, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)


def record(title, args, filename):
    command = 'python '+' '.join(args)
    result = subprocess.run([sys.executable, *args], cwd=ROOT, text=True,
                            encoding='utf-8', errors='replace', stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    if result.returncode:
        raise RuntimeError(result.stdout+'\n'+result.stderr)
    transcript = result.stdout.strip()
    (OUTPUT/(filename+'.txt')).write_text('$ '+command+'\n\n'+transcript+'\n', encoding='utf-8')
    if result.stderr:
        # Keep warnings in the transcript rather than hiding them from learners.
        with (OUTPUT/(filename+'.txt')).open('a', encoding='utf-8') as stream:
            stream.write('\nWarnings / diagnostic output:\n'+result.stderr)
    animate(title, command, transcript, OUTPUT/(filename+'.gif'))
    print(transcript, flush=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    record('1 / Train the fruit model', ['scripts/train_fruit.py', '--output', '.cache/fruit-training'], 'train-fruit')
    record('2 / Export the trained model to .pte', ['scripts/export_fruit.py', '--parameters',
           '.cache/fruit-training/fruit_parameters.json', '--output', '.cache/fruit-export'], 'export-fruit')
    # Verify the output advertised in the animation exists and matches its contract.
    import hashlib
    contract = json.loads((ROOT/'.cache/fruit-export/fruit_contract.json').read_text(encoding='utf-8'))
    model = ROOT/'.cache/fruit-export/fruit_classifier.pte'
    assert hashlib.sha256(model.read_bytes()).hexdigest() == contract['sha256']
    print('Saved verified tutorial GIFs and transcripts to', OUTPUT, flush=True)


if __name__ == '__main__':
    main()
