"""Train the fruit classifier separately from exporting it to ExecuTorch."""
import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from export_fruit import CACHE, CLASSES, pixels, prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.cache/fruit-training'))
    parser.add_argument('--c', type=float, default=0.1, help='Inverse regularization strength')
    parser.add_argument('--max-iter', type=int, default=1000)
    args = parser.parse_args()
    if not np.isfinite(args.c) or args.c <= 0 or args.max_iter < 1:
        parser.error('--c must be finite and positive; --max-iter must be positive')

    manifest = prepare()
    labels = [label for label, _ in CLASSES]
    groups = {}
    for split in ['Training', 'Test']:
        records = [r for r in manifest['images'] if r['split'] == split]
        images = np.stack([pixels(CACHE/r['path']) for r in records])
        targets = np.array([labels.index(r['label']) for r in records])
        groups[split] = (images.reshape(len(records), -1)*2-1, targets)
    print('Training: 360 photos | Testing: 120 separate photos', flush=True)
    print(f'Logistic regression: C={args.c}, max_iter={args.max_iter}, solver=lbfgs, tol=0.0001', flush=True)
    classifier = LogisticRegression(C=args.c, max_iter=args.max_iter, random_state=42,
                                    solver='lbfgs', tol=1e-4)
    classifier.fit(*groups['Training'])
    accuracy = float(classifier.score(*groups['Test']))
    print(f'Test accuracy: {accuracy:.2%} (dataset subset, not general camera accuracy)', flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    parameters = dict(weights=classifier.coef_.tolist(), bias=classifier.intercept_.tolist())
    report = dict(labels=labels, training_samples=len(groups['Training'][1]),
                  test_samples=len(groups['Test'][1]), held_out_accuracy=accuracy,
                  dataset_revision=manifest['revision'], C=args.c, max_iter=args.max_iter,
                  solver='lbfgs', tol=1e-4, random_state=42,
                  iterations=classifier.n_iter_.tolist())
    (args.output/'fruit_parameters.json').write_text(json.dumps(parameters, indent=2), encoding='utf-8')
    (args.output/'training_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Saved:', args.output/'fruit_parameters.json', flush=True)
    print('Next: export these learned parameters to a .pte file.', flush=True)


if __name__ == '__main__':
    main()
