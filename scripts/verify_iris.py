"""Verify trained example numerics and the generated App Inventor blocks."""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as E
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
    params=json.loads((ROOT/'models/iris_parameters.json').read_text(encoding='utf-8'))
    contract=json.loads((ROOT/'models/iris_contract.json').read_text(encoding='utf-8'))
    fixtures=json.loads((ROOT/'models/iris_test_fixtures.json').read_text(encoding='utf-8'))
    def predict(x):
        x=(np.asarray(x)-params['mean'])/params['scale']
        logits=x@np.asarray(params['weights']).T+params['bias'];p=np.exp(logits-logits.max(axis=-1,keepdims=True));return p/p.sum(axis=-1,keepdims=True)
    scores=predict(fixtures['inputs'])
    np.testing.assert_allclose(scores,fixtures['expected_probabilities'],atol=2e-6)
    assert (scores.argmax(axis=1)==fixtures['targets']).mean()>=.90
    assert len(set(fixtures['train_indices'])&set(fixtures['test_indices']))==0
    for preset in contract['presets']:
        assert contract['labels'][int(predict([preset['values']]).argmax())]==preset['label']
    assert hashlib.sha256((ROOT/'models/iris_classifier.pte').read_bytes()).hexdigest()==contract['sha256']
    with zipfile.ZipFile(ROOT/'examples/ExecuTorchIris.aia') as z:
        assert z.testzip() is None
        assert z.read('assets/iris_classifier.pte')==(ROOT/'models/iris_classifier.pte').read_bytes()
        scm=z.read(next(n for n in z.namelist() if n.endswith('.scm'))).decode()
        project=json.loads(scm.split('$JSON\n',1)[1].rsplit('\n|#',1)[0])
        components={c['$Name']:c for c in project['Properties']['$Components']}
        assert components['ExecuTorch1']['$Type']=='ExecuTorch'
        assert all(n in components for n in ['ClassifyButton','SetosaButton','VersicolorButton','VirginicaButton','ExecuTorch1'])
        tree=E.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.bky'))))
        ns={'b':'https://developers.google.com/blockly/xml'}
        for b in tree.findall('.//b:block',ns):
            mutation=b.find('b:mutation',ns)
            if b.get('type','').startswith('component_'):
                assert mutation.get('instance_name')=='Screen1' or mutation.get('instance_name') in components
        calls=tree.findall('.//b:block[@type="component_method"]/b:mutation',ns)
        assert {c.get('method_name') for c in calls}=={'LoadModel','RunModel'}
        assert b'iris_classifier.pte' in E.tostring(tree)
        errors=next(b for b in tree.findall('b:block',ns)
                    if b.find('b:mutation',ns).get('event_name')=='ErrorOccurred')
        enabled=next(b for b in errors.findall('.//b:block',ns)
                     if b.get('type')=='component_set_get'
                     and b.find('b:mutation',ns).get('property_name')=='Enabled')
        condition=enabled.find('b:value/b:block',ns)
        assert condition.get('type')=='logic_compare'
        assert condition.find('b:field[@name="OP"]',ns).text=='NEQ'
        assert condition.find('b:value[@name="B"]/b:block/b:field',ns).text=='LoadModel'
    print('PASS: 30 held-out fixtures, 3 presets, disjoint split, PTE hash, AIA assets and component wiring')
    print('Native PTE execution and Android behaviour still require device testing.')
if __name__=='__main__': main()
