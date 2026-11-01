"""Draw the extension's blocks and write docs/blocks.md from the built AIX metadata.

Run after scripts/build.py. The pictures and tables come from components.json inside
out/org.community.executorch.aix, so they stay in step with the Java source. Parameter
meanings live in PARAMETERS below; the script stops if the API gains a parameter that
has no entry there.
"""
from pathlib import Path
import json, subprocess, shutil, zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images/blocks'
INSTANCE = 'ExecuTorch1'

# What each parameter means in plain words. Keyed by "Block.parameter".
PARAMETERS = {
    'LoadModel.assetName': 'Exact filename of the `.pte` in the project Media, for example `fruit_classifier.pte`.',
    'RunImage.imagePath': 'A Media asset name (`apple.jpg`), an ImagePicker `Selection`, or the `image` path from `Camera.AfterPicture`.',
    'RunImage.size': 'Side length in pixels. The photo is stretched to `size × size`; the fruit model uses 32.',
    'RunModel.values': 'Flat list of numbers in row-major order. For a `[1, 4]` tensor, four numbers.',
    'RunModel.shape': 'List of positive whole numbers whose product equals the length of `values`. An empty list means a single scalar.',
    'ModelLoaded.assetName': 'The filename that was loaded. The fruit app shows it on screen.',
    'InferenceCompleted.values': 'Flat list of float32 outputs. For the fruit model: three scores in apple, banana, orange order (list positions 1, 2, 3).',
    'InferenceCompleted.shape': 'Shape of the output tensor, for example `[1, 3]`.',
    'InferenceCompleted.elapsedMs': 'Inference time in milliseconds, measured on the phone.',
    'ErrorOccurred.operation': 'Which block failed: `LoadModel`, `RunImage`, `RunModel` or `UnloadModel`.',
    'ErrorOccurred.message': 'The original error text from the extension or the native runtime. Include it when reporting a problem.',
}

# Extra notes shown under each block.
NOTES = {
    'LoadModel': 'Call once, usually in `Screen.Initialize`. Wait for `ModelLoaded` before running anything. If loading fails you get `ErrorOccurred` with operation `LoadModel`, and the previous model, if any, stays loaded.',
    'RunImage': 'For image models that take RGB float32 NCHW input in `[0, 1]`. Any further normalization must be inside the model. Finishes with `InferenceCompleted` or `ErrorOccurred`.',
    'RunModel': 'For any model that takes one float32 tensor. Finishes with `InferenceCompleted` or `ErrorOccurred`. Wait for the result before sending the next call; the queue holds four.',
    'UnloadModel': 'Frees the native memory. Raises `ModelUnloaded`. Call `LoadModel` again before the next inference.',
    'ModelLoaded': 'Enable your inference buttons here.',
    'ModelUnloaded': 'The model has been released; inference calls will fail until you load one.',
    'InferenceCompleted': 'Read scores with the `select list item` block. Scores are probabilities only if the model ends in softmax, as the fruit model does.',
    'ErrorOccurred': 'Show `message` to the user. The fruit app treats a `LoadModel` error specially: it disables the photo controls and offers a retry.',
}

METHOD, EVENT, PARAM, TEXT = '#7C5CBF', '#B6872C', '#E3A24C', '#FFFFFF'
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=15, fill=TEXT, weight='normal', anchor='start'):
    return f"<text x='{x}' y='{y}' font-size='{size}' fill='{fill}' font-weight='{weight}' text-anchor='{anchor}' {FONT}>{esc(s)}</text>"


def method_svg(name, params):
    rows = max(1, len(params))
    row_h, head = 30, 38
    w = max(300, 8 * len(f'{INSTANCE}.{name}') + 110 + max([8 * len(p['name']) for p in params] or [0]))
    h = head + (rows - 1) * row_h + 16
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w + 20}' height='{h + 20}' viewBox='0 0 {w + 20} {h + 20}'>"]
    # body with top notch and bottom tab
    s.append(f"<path d='M10,10 h20 v6 h20 v-6 h{w - 40} v{h} h-{w - 40} v6 h-20 v-6 h-20 z' fill='{METHOD}' stroke='#5E4295' stroke-width='1.5'/>")
    s.append(text(22, 36, 'call', 15, TEXT, 'bold'))
    s.append(text(60, 36, f'{INSTANCE}.{name}', 15))
    for i, p in enumerate(params):
        y = 36 + i * row_h
        s.append(text(w - 30, y, p['name'], 14, TEXT, 'normal', 'end'))
        # input socket
        s.append(f"<path d='M{w + 10},{y - 16} h-10 v6 h-6 v8 h6 v6 h10 z' fill='#F3EEFA' stroke='#5E4295' stroke-width='1'/>")
    s.append('</svg>')
    return '\n'.join(s)


def event_svg(name, params):
    head, inner, foot = 46, 40, 22
    h = head + inner + foot
    chips = []
    x = 72 + 8 * len(f'{INSTANCE}.{name}') + 18
    for p in params:
        pw = 8 * len(p['name']) + 18
        chips.append((x, pw, p['name']))
        x += pw + 8
    w = max(340, x + 10)
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w + 20}' height='{h + 20}' viewBox='0 0 {w + 20} {h + 20}'>"]
    # hat-shaped event block with a C mouth
    s.append(f"<path d='M10,20 q30,-20 60,0 h{w - 60} v{head - 10} h-{w - 40} v{inner} h{w - 40} v{foot} h-{w} z' fill='{EVENT}' stroke='#8A6520' stroke-width='1.5'/>")
    s.append(text(22, 50, 'when', 15, TEXT, 'bold'))
    s.append(text(72, 50, f'{INSTANCE}.{name}', 15))
    for cx, pw, label in chips:
        s.append(f"<rect x='{cx}' y='34' width='{pw}' height='22' rx='11' fill='{PARAM}' stroke='#9C6A24'/>")
        s.append(text(cx + pw / 2, 50, label, 13, '#3A2A10', 'normal', 'middle'))
    s.append(text(22, head + 26, 'do', 15, TEXT, 'bold'))
    s.append('</svg>')
    return '\n'.join(s)


def main():
    with zipfile.ZipFile(ROOT / 'out/org.community.executorch.aix') as aix:
        api = json.loads(aix.read('org.community.executorch/components.json'))[0]
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('*'):
        old.unlink()
    convert = shutil.which('magick') or shutil.which('convert')

    def picture(stem, svg):
        (OUT / f'{stem}.svg').write_text(svg, encoding='utf-8')
        if convert:
            subprocess.run([convert, '-density', '144', '-background', 'none', str(OUT / f'{stem}.svg'), str(OUT / f'{stem}.png')], check=True)
            return f'images/blocks/{stem}.png'
        return f'images/blocks/{stem}.svg'

    lines = [
        '# Block reference',
        '',
        f"Every block the ExecuTorch component adds to App Inventor (extension version {api['version']}). "
        'The pictures and tables are generated from the built extension by `python scripts/make_block_reference.py`; '
        'edit the Java source or that script, not this page.',
        '',
        f"{api['helpString']}",
        '',
        'Drag **ExecuTorch** from the Extension drawer onto the screen; it appears as a non-visible component. '
        'In the Blocks editor, click `ExecuTorch1` to find the blocks below. The purple blocks are calls you make; '
        'the gold blocks are events that run when the extension has something to report.',
        '',
        '## Calls',
        '',
    ]
    for m in sorted(api['methods'], key=lambda m: ['LoadModel', 'RunImage', 'RunModel', 'UnloadModel'].index(m['name'])):
        pic = picture(f"call-{m['name']}", method_svg(m['name'], m['params']))
        lines += [f"### {m['name']}", '', f"![call {INSTANCE}.{m['name']}]({pic})", '', m['description'], '']
        if m['params']:
            lines += ['| Parameter | Type | Meaning |', '| --- | --- | --- |']
            for p in m['params']:
                key = f"{m['name']}.{p['name']}"
                assert key in PARAMETERS, f'Add a description for {key} to PARAMETERS'
                lines.append(f"| `{p['name']}` | {p['type']} | {PARAMETERS[key]} |")
            lines.append('')
        else:
            lines += ['No parameters.', '']
        lines += [NOTES[m['name']], '']
    lines += ['## Events', '']
    for e in sorted(api['events'], key=lambda e: ['ModelLoaded', 'InferenceCompleted', 'ErrorOccurred', 'ModelUnloaded'].index(e['name'])):
        pic = picture(f"event-{e['name']}", event_svg(e['name'], e['params']))
        lines += [f"### {e['name']}", '', f"![when {INSTANCE}.{e['name']}]({pic})", '', e['description'], '']
        if e['params']:
            lines += ['| Parameter | Type | Meaning |', '| --- | --- | --- |']
            for p in e['params']:
                key = f"{e['name']}.{p['name']}"
                assert key in PARAMETERS, f'Add a description for {key} to PARAMETERS'
                lines.append(f"| `{p['name']}` | {p['type']} | {PARAMETERS[key]} |")
            lines += ['', 'Use the parameter blocks by name (`message`, not `get message`) inside the event.', '']
        else:
            lines += ['No parameters.', '']
        lines += [NOTES[e['name']], '']
    lines += [
        '## How the fruit app wires them together',
        '',
        '```text',
        'when Screen1.Initialize',
        '    call ExecuTorch1.LoadModel  assetName: "fruit_classifier.pte"',
        '',
        'when ExecuTorch1.ModelLoaded (assetName)',
        '    enable the sample and photo buttons; show assetName on screen',
        '',
        'when AppleButton.Click',
        '    call ExecuTorch1.RunImage  imagePath: "apple.jpg"  size: 32',
        '',
        'when ExecuTorch1.InferenceCompleted (values, shape, elapsedMs)',
        '    compare select list item values 1, 2 and 3; show the largest label and elapsedMs',
        '',
        'when ExecuTorch1.ErrorOccurred (operation, message)',
        '    if operation = "LoadModel": disable the buttons, show message, show Retry',
        '    else: show operation and message',
        '```',
        '',
        'Open `examples/ExecuTorchFruit.aia` in App Inventor and switch to **Blocks** to see the real thing. '
        'The [learning guide](learning-guide.md) walks through one prediction and the '
        '[developer guide](developer-guide.md) has the model contract these blocks expect.',
        '',
    ]
    (ROOT / 'docs/blocks.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    print('Wrote docs/blocks.md and', len(list(OUT.iterdir())), 'images')


if __name__ == '__main__':
    main()
