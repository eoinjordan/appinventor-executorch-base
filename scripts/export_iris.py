"""Reproducible training/export; not needed to use the checked-in beginner example."""
from pathlib import Path
import hashlib
import json
import numpy as np
import sklearn
import torch
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from executorch.exir import to_edge

ROOT = Path(__file__).resolve().parents[1]

class IrisModel(torch.nn.Module):
    def __init__(self, mean, scale, weights, bias):
        super().__init__()
        for name, value in [('mean', mean), ('scale', scale), ('weights', weights), ('bias', bias)]:
            self.register_buffer(name, torch.tensor(value, dtype=torch.float32))

    def forward(self, measurements):
        normalized = (measurements - self.mean) / self.scale
        return torch.softmax(torch.nn.functional.linear(normalized, self.weights, self.bias), dim=1)

def main():
    dataset = load_iris()
    train, test = train_test_split(np.arange(150), test_size=0.2, stratify=dataset.target, random_state=42)
    scaler = StandardScaler().fit(dataset.data[train])
    classifier = LogisticRegression(C=10.0, max_iter=1000, random_state=42)
    classifier.fit(scaler.transform(dataset.data[train]), dataset.target[train])
    params = dict(mean=scaler.mean_.tolist(), scale=scaler.scale_.tolist(),
                  weights=classifier.coef_.tolist(), bias=classifier.intercept_.tolist())
    model = IrisModel(**params).eval()
    with torch.no_grad():
        probabilities = model(torch.tensor(dataset.data[test], dtype=torch.float32)).numpy()
    np.testing.assert_allclose(probabilities, classifier.predict_proba(scaler.transform(dataset.data[test])), atol=2e-6)
    accuracy = float((probabilities.argmax(axis=1) == dataset.target[test]).mean())
    assert accuracy >= .90
    presets = [dict(label='setosa', values=[5.1, 3.5, 1.4, .2]),
               dict(label='versicolor', values=[6.0, 2.9, 4.5, 1.5]),
               dict(label='virginica', values=[6.5, 3.0, 5.8, 2.2])]
    labels = dataset.target_names.tolist()
    for preset in presets:
        scores = model(torch.tensor([preset['values']], dtype=torch.float32)).detach().numpy()[0]
        assert labels[int(scores.argmax())] == preset['label']
        preset['expected_probabilities'] = scores.tolist()
    exported = torch.export.export(model, (torch.zeros(1, 4),))
    # Compare the exported PyTorch graph with the original before serializing PTE.
    with torch.no_grad():
        torch.testing.assert_close(exported.module()(torch.tensor(dataset.data[test[:1]], dtype=torch.float32)),
                                   model(torch.tensor(dataset.data[test[:1]], dtype=torch.float32)))
    buffer = to_edge(exported).to_executorch().buffer
    out = ROOT / 'models'
    (out/'iris_classifier.pte').write_bytes(buffer)
    (out/'iris_parameters.json').write_text(json.dumps(params, indent=2))
    (out/'iris_contract.json').write_text(json.dumps(dict(
        model='iris_classifier.pte', runtime='1.5.1', input_shape=[1,4], output_shape=[1,3], dtype='float32',
        features=['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)'],
        labels=labels, preprocessing='Included in model; pass raw centimetres in feature order.',
        presets=presets, source='https://archive.ics.uci.edu/dataset/53/iris', sha256=hashlib.sha256(buffer).hexdigest()), indent=2))
    fixtures = dict(train_indices=train.tolist(), test_indices=test.tolist(),
                    inputs=dataset.data[test].tolist(), targets=dataset.target[test].tolist(),
                    expected_probabilities=probabilities.tolist(), held_out_accuracy=accuracy,
                    torch_version=torch.__version__, sklearn_version=sklearn.__version__,
                    native_pte_inference='Not verified on host: incompatible ExecuTorch native DLL.')
    (out/'iris_test_fixtures.json').write_text(json.dumps(fixtures, indent=2))
    print(f'Exported {len(buffer)} byte PTE; held-out eager accuracy {accuracy:.1%} on {len(test)} samples')

if __name__ == '__main__':
    main()
