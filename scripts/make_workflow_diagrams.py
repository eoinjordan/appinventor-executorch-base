"""Write docs/blocks-workflow.drawio and the PNG/SVG renders the docs embed.

Each diagram is defined once below as boxes and arrows. The same data produces an
editable draw.io file (open it at https://app.diagrams.net) and the pictures under
docs/images/blocks/, so the two cannot drift apart. Styles match architecture.drawio.
"""
from pathlib import Path
import shutil, subprocess
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images/blocks'
DRAWIO = ROOT / 'docs/blocks-workflow.drawio'

# Fill colours, shared with architecture.drawio.
UI, CALL, EVENT, ERROR, NOTE = '#d5e8d4', '#e1d5e7', '#fff2cc', '#f8cecc', '#ffffff'
W, H = 220, 60


def box(id, x, y, text, fill, w=W, h=H):
    return dict(id=id, x=x, y=y, w=w, h=h, text=text, fill=fill)


def arrow(src, dst, label='', dashed=False, points=()):
    return dict(src=src, dst=dst, label=label, dashed=dashed, points=list(points))


SETUP = dict(
    id='setup', name='Adding the extension', title='Adding the ExecuTorch extension to a project',
    boxes=[
        box('import', 40, 120, 'Extensions > Import extension\nExecuTorch-ARM64.aix', UI),
        box('drag', 320, 120, 'Drag ExecuTorch onto Screen1\n(non-visible component)', UI),
        box('media', 600, 120, 'Media > Upload File\nyour .pte and sample images', UI),
        box('blocks', 880, 120, 'Blocks\nLoadModel, then the events', CALL),
        box('build', 1160, 120, 'Build > Android App (.apk)\ninstall on a 64-bit phone', UI),
    ],
    arrows=[arrow('import', 'drag'), arrow('drag', 'media'), arrow('media', 'blocks'), arrow('blocks', 'build')],
)

RUN = dict(
    id='run', name='How the blocks run', title='How the ExecuTorch blocks run',
    boxes=[
        box('init', 440, 40, 'Screen1.Initialize', UI),
        box('load', 440, 150, 'call LoadModel(assetName)', CALL),
        box('loaded', 440, 260, 'ModelLoaded(assetName)', EVENT),
        box('enable', 440, 370, 'Enable your buttons', UI),
        box('trigger', 440, 480, 'Button.Click, ImagePicker.AfterPicking\nor Camera.AfterPicture', UI),
        box('runimage', 200, 600, 'call RunImage(imagePath, size)', CALL),
        box('runmodel', 680, 600, 'call RunModel(values, shape)', CALL),
        box('done', 440, 720, 'InferenceCompleted\n(values, shape, elapsedMs)', EVENT),
        box('show', 440, 830, 'Pick the largest score,\nshow its label', UI),
        box('unload', 920, 370, 'call UnloadModel()', CALL),
        box('unloaded', 920, 480, 'ModelUnloaded()', EVENT),
        box('error', 1000, 720, 'ErrorOccurred\n(operation, message)', ERROR),
    ],
    arrows=[
        arrow('init', 'load'), arrow('load', 'loaded'), arrow('loaded', 'enable'), arrow('enable', 'trigger'),
        arrow('trigger', 'runimage'), arrow('trigger', 'runmodel'),
        arrow('runimage', 'done'), arrow('runmodel', 'done'), arrow('done', 'show'),
        arrow('show', 'trigger', 'next photo', points=[(120, 860), (120, 510)]),
        arrow('enable', 'unload'), arrow('unload', 'unloaded'),
        arrow('unloaded', 'load', 'load another model', points=[(1260, 510), (1260, 165)]),
        arrow('load', 'error', 'failure', dashed=True, points=[(1110, 195)]),
        arrow('runimage', 'error', 'failure', dashed=True, points=[(310, 690), (1110, 690)]),
        arrow('runmodel', 'error', 'failure', dashed=True, points=[(790, 690), (1110, 690)]),
    ],
)

DIAGRAMS = [SETUP, RUN]


def centre(b):
    return b['x'] + b['w'] / 2, b['y'] + b['h'] / 2


def edge_point(b, towards):
    """Where a straight line from the box centre towards a point leaves the box."""
    cx, cy = centre(b)
    dx, dy = towards[0] - cx, towards[1] - cy
    if dx == dy == 0:
        return cx, cy
    sx = (b['w'] / 2) / abs(dx) if dx else float('inf')
    sy = (b['h'] / 2) / abs(dy) if dy else float('inf')
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def drawio_page(d):
    cells = ['<mxCell id="0" />', '<mxCell id="1" parent="0" />']
    width = max(b['x'] + b['w'] for b in d['boxes']) + 40
    cells.append(f'<mxCell id="{d["id"]}-title" value="{escape(d["title"])}" vertex="1" parent="1" '
                 f'style="rounded=1;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor=none;fontSize=20;fontStyle=1;spacing=10;">'
                 f'<mxGeometry x="30" y="-40" width="{width - 60}" height="50" as="geometry" /></mxCell>')
    for b in d['boxes']:
        cells.append(f'<mxCell id="{d["id"]}-{b["id"]}" value="{escape(b["text"])}" vertex="1" parent="1" '
                     f'style="rounded=1;whiteSpace=wrap;html=0;fillColor={b["fill"]};strokeColor=#666666;fontSize=14;spacing=10;">'
                     f'<mxGeometry x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" as="geometry" /></mxCell>')
    for i, a in enumerate(d['arrows']):
        dash = 'dashed=1;strokeColor=#b85450;' if a['dashed'] else ''
        pts = ''.join(f'<mxPoint x="{x}" y="{y}" />' for x, y in a['points'])
        array = '<Array as="points">' + pts + '</Array>' if pts else ''
        geometry = f'<mxGeometry relative="1" as="geometry">{array}</mxGeometry>'
        cells.append(f'<mxCell id="{d["id"]}-a{i}" value="{escape(a["label"])}" edge="1" parent="1" '
                     f'source="{d["id"]}-{a["src"]}" target="{d["id"]}-{a["dst"]}" '
                     f'style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;endFill=1;fontSize=12;labelBackgroundColor=#ffffff;{dash}">'
                     f'{geometry}</mxCell>')
    return (f'<diagram id="{d["id"]}" name="{escape(d["name"])}"><mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" '
            f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1000" '
            f'math="0" shadow="0"><root>{"".join(cells)}</root></mxGraphModel></diagram>')


def svg(d):
    boxes = {b['id']: b for b in d['boxes']}
    width = max([b['x'] + b['w'] for b in d['boxes']] + [x for a in d['arrows'] for x, _ in a['points']]) + 40
    height = max([b['y'] + b['h'] for b in d['boxes']] + [y for a in d['arrows'] for _, y in a['points']]) + 40
    font = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
         "<defs><marker id='arrow' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='8' markerHeight='8' orient='auto-start-reverse'>"
         "<path d='M0,0 L10,5 L0,10 z' fill='#666666'/></marker>"
         "<marker id='arrow-red' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='8' markerHeight='8' orient='auto-start-reverse'>"
         "<path d='M0,0 L10,5 L0,10 z' fill='#b85450'/></marker></defs>",
         f"<rect width='{width}' height='{height}' fill='#ffffff'/>"]
    for a in d['arrows']:
        src, dst = boxes[a['src']], boxes[a['dst']]
        first = a['points'][0] if a['points'] else centre(dst)
        last = a['points'][-1] if a['points'] else centre(src)
        pts = [edge_point(src, first)] + a['points'] + [edge_point(dst, last)]
        colour = '#b85450' if a['dashed'] else '#666666'
        dash = " stroke-dasharray='6,4'" if a['dashed'] else ''
        s.append(f"<polyline points='{' '.join(f'{x:.0f},{y:.0f}' for x, y in pts)}' fill='none' stroke='{colour}' stroke-width='1.5'{dash}/>")
        # Arrowhead drawn by hand: SVG markers are not supported by every rasteriser.
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        dx, dy = x2 - x1, y2 - y1
        length = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / length, dy / length
        bx, by = x2 - 12 * ux, y2 - 12 * uy
        s.append(f"<polygon points='{x2:.0f},{y2:.0f} {bx - 5 * uy:.0f},{by + 5 * ux:.0f} {bx + 5 * uy:.0f},{by - 5 * ux:.0f}' fill='{colour}'/>")
        if a['label']:
            seg = max(zip(pts, pts[1:]), key=lambda q: abs(q[1][0] - q[0][0]) + abs(q[1][1] - q[0][1]))
            mid = ((seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2)
            tw = 7 * len(a['label']) + 10
            s.append(f"<rect x='{mid[0] - tw / 2:.0f}' y='{mid[1] - 9:.0f}' width='{tw}' height='18' fill='#ffffff'/>")
            s.append(f"<text x='{mid[0]:.0f}' y='{mid[1] + 4:.0f}' font-size='12' fill='#333333' text-anchor='middle' {font}>{escape(a['label'])}</text>")
    for b in d['boxes']:
        s.append(f"<rect x='{b['x']}' y='{b['y']}' width='{b['w']}' height='{b['h']}' rx='8' fill='{b['fill']}' stroke='#666666' stroke-width='1.2'/>")
        lines = b['text'].split('\n')
        cx, cy = centre(b)
        y0 = cy - (len(lines) - 1) * 9
        for i, line in enumerate(lines):
            s.append(f"<text x='{cx}' y='{y0 + i * 18 + 5:.0f}' font-size='14' fill='#222222' text-anchor='middle' {font}>{escape(line)}</text>")
    s.append('</svg>')
    return '\n'.join(s)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = ''.join(drawio_page(d) for d in DIAGRAMS)
    DRAWIO.write_text("<?xml version='1.0' encoding='utf-8'?>\n<mxfile host=\"app.diagrams.net\" type=\"device\" version=\"24.7.17\">"
                      + pages + '</mxfile>\n', encoding='utf-8', newline='\n')
    convert = shutil.which('magick') or shutil.which('convert')
    for d in DIAGRAMS:
        stem = OUT / f"{d['id']}-workflow"
        stem.with_suffix('.svg').write_text(svg(d), encoding='utf-8')
        if convert:
            subprocess.run([convert, '-density', '144', '-background', 'white', '-define', 'png:exclude-chunk=date,time', '-strip',
                            str(stem.with_suffix('.svg')), str(stem.with_suffix('.png'))], check=True)
    print('Wrote', DRAWIO.relative_to(ROOT), 'and', len(DIAGRAMS), 'diagram renders')


if __name__ == '__main__':
    main()
