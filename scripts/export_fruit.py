"""Train a small fruit photo model using a pinned Fruits-360 subset.

Training/export is optional: the model and example photos are checked in.
"""
from pathlib import Path
import hashlib, json, shutil, zipfile
import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
import torch
from executorch.exir import to_edge

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/'.cache/fruits'
REPO = 'fruits-360/fruits-360-100x100'
CLASSES = [('apple', 'Apple Red 1'), ('banana', 'Banana 1'), ('orange', 'Orange 1')]
SIZE = 32

def prepare():
    # Use the checked-in, pinned subset: training does not depend on upstream HEAD.
    manifest=json.loads((ROOT/'models/fruit_dataset_manifest.json').read_text())
    with zipfile.ZipFile(ROOT/'models/fruit_dataset.zip') as archive:
        for record in manifest['images']:
            relative=Path(record['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Invalid dataset path')
            data=archive.read(record['path'])
            if hashlib.sha256(data).hexdigest()!=record['sha256']:
                raise ValueError('Dataset hash mismatch: '+record['path'])
            target=CACHE/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
    print('Verified bundled dataset:',len(manifest['images']),'images',flush=True)
    return manifest


def pixels(path):
    with Image.open(path) as image:
        return np.asarray(image.convert('RGB').resize((SIZE,SIZE),Image.Resampling.BILINEAR),dtype=np.float32).transpose(2,0,1)/255

class FruitModel(torch.nn.Module):
    def __init__(self, weights, bias):
        super().__init__()
        self.register_buffer('weights',torch.tensor(weights,dtype=torch.float32))
        self.register_buffer('bias',torch.tensor(bias,dtype=torch.float32))
    def forward(self,image):
        features=image.reshape(image.shape[0],3*SIZE*SIZE)*2-1
        return torch.softmax(torch.nn.functional.linear(features,self.weights,self.bias),dim=1)

def main():
    manifest=prepare(); labels=[name for name,_ in CLASSES]
    train=[r for r in manifest['images'] if r['split']=='Training']
    test=[r for r in manifest['images'] if r['split']=='Test']
    assert not {r['path'] for r in train} & {r['path'] for r in test}
    x_train=np.stack([pixels(CACHE/r['path']) for r in train])
    y_train=np.array([labels.index(r['label']) for r in train])
    x_test=np.stack([pixels(CACHE/r['path']) for r in test])
    y_test=np.array([labels.index(r['label']) for r in test])
    classifier=LogisticRegression(C=.1,max_iter=1000,random_state=42)
    classifier.fit(x_train.reshape(len(train),-1)*2-1,y_train)
    params=dict(weights=classifier.coef_.tolist(),bias=classifier.intercept_.tolist())
    model=FruitModel(**params).eval()
    with torch.no_grad(): scores=model(torch.from_numpy(x_test)).numpy()
    np.testing.assert_allclose(scores,classifier.predict_proba(x_test.reshape(len(test),-1)*2-1),atol=2e-5)
    accuracy=float((scores.argmax(1)==y_test).mean()); assert accuracy>=.90, accuracy
    output=ROOT/'models'; samples=output/'fruit_samples'; samples.mkdir(exist_ok=True)
    presets=[]
    for label in labels:
        for i,record in enumerate(test):
            if record['label']==label and int(scores[i].argmax())==labels.index(label):
                name=label+'.jpg'; shutil.copyfile(CACHE/record['path'],samples/name)
                presets.append(dict(label=label,file=name,source=record['url'],sha256=record['sha256'],expected_probabilities=scores[i].tolist()))
                break
    exported=torch.export.export(model,(torch.zeros(1,3,SIZE,SIZE),))
    torch.testing.assert_close(exported.module()(torch.from_numpy(x_test[:1])),model(torch.from_numpy(x_test[:1])))
    buffer=to_edge(exported).to_executorch().buffer
    (output/'fruit_classifier.pte').write_bytes(buffer)
    (output/'fruit_parameters.json').write_text(json.dumps(params))
    contract=dict(model='fruit_classifier.pte',runtime='1.5.1',size=SIZE,input_shape=[1,3,SIZE,SIZE],output_shape=[1,3],dtype='float32',labels=labels,preprocessing='Stretch resize; RGB NCHW /255. Remaining normalization is inside the model.',samples=presets,training_samples=len(train),test_samples=len(test),held_out_accuracy=accuracy,sha256=hashlib.sha256(buffer).hexdigest(),dataset_revision=manifest['revision'],scope='Three Fruits-360 varieties photographed as isolated fruit on white backgrounds. Scores are relative probabilities within these three classes; arbitrary objects and everyday backgrounds are not validated.')
    (output/'fruit_contract.json').write_text(json.dumps(contract,indent=2))
    (output/'fruit_dataset_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(f'Exported {len(buffer)} byte PTE; eager test accuracy {accuracy:.2%} on {len(test)} official Test images',flush=True)

if __name__=='__main__': main()
