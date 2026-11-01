"""Check model/photo fixtures, dataset separation and actual AIA block signatures."""
from pathlib import Path
import hashlib, json, zipfile, xml.etree.ElementTree as E
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
contract=json.loads((ROOT/'models/fruit_contract.json').read_text(encoding='utf-8'))
params=json.loads((ROOT/'models/fruit_parameters.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'models/fruit_dataset_manifest.json').read_text(encoding='utf-8'))
train=[r for r in manifest['images'] if r['split']=='Training']
test=[r for r in manifest['images'] if r['split']=='Test']
assert len(train)==360 and len(test)==120
assert not {r['path'] for r in train} & {r['path'] for r in test}
assert not {r['sha256'] for r in train} & {r['sha256'] for r in test}
assert contract['dataset_revision']==manifest['revision']
assert contract['labels']==['apple','banana','orange']
assert contract['held_out_accuracy']>=.90
assert hashlib.sha256((ROOT/'models/fruit_classifier.pte').read_bytes()).hexdigest()==contract['sha256']
with zipfile.ZipFile(ROOT/'models/fruit_dataset.zip') as dataset:
    assert dataset.testzip() is None
    assert json.loads(dataset.read('manifest.json'))==manifest
    assert b'CC BY-SA 4.0' in dataset.read('ATTRIBUTION.md')
    for record in manifest['images']:
        assert hashlib.sha256(dataset.read(record['path'])).hexdigest()==record['sha256']
for sample in contract['samples']:
    path=ROOT/'models/fruit_samples'/sample['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==sample['sha256']
    with Image.open(path) as image:
        x=np.asarray(image.convert('RGB').resize((32,32),Image.Resampling.BILINEAR),dtype=float).transpose(2,0,1).reshape(1,-1)/255
    logits=(x*2-1)@np.asarray(params['weights']).T+params['bias']
    p=np.exp(logits-logits.max());p/=p.sum()
    np.testing.assert_allclose(p[0],sample['expected_probabilities'],atol=2e-5)
    assert contract['labels'][int(p.argmax())]==sample['label']
with zipfile.ZipFile(ROOT/'examples/ExecuTorchFruit.aia') as z:
    assert z.testzip() is None
    assert z.read('assets/fruit_classifier.pte')==(ROOT/'models/fruit_classifier.pte').read_bytes()
    assert b'CC BY-SA 4.0' in z.read('assets/FRUIT_ATTRIBUTION.txt')
    scm=z.read(next(n for n in z.namelist() if n.endswith('.scm'))).decode()
    project=json.loads(scm.split('$JSON\n',1)[1].rsplit('\n|#',1)[0])
    def descendants(items):
        for item in items:
            yield item
            yield from descendants(item.get('$Components',[]))
    components={c['$Name']:c for c in descendants(project['Properties']['$Components'])}
    api=json.loads(z.read('assets/external_comps/org.community.executorch/components.json'))[0]
    build_info=json.loads(z.read('assets/external_comps/org.community.executorch/files/component_build_infos.json'))[0]
    assert build_info['native']==[], 'Bundled extension must avoid AttachNativeLibs metadata failure'
    assert components['ExecuTorch1']['$Type']==api['name']=='ExecuTorch'
    assert int(components['ExecuTorch1']['$Version'])==int(api['version'])
    assert {'AppleButton','BananaButton','OrangeButton','ChoosePhoto','Camera1'}<=components.keys()
    methods={m['name']:m for m in api['methods']}; events={e['name']:e for e in api['events']}
    tree=E.fromstring(z.read(next(n for n in z.namelist() if n.endswith('.bky'))))
    ns={'b':'https://developers.google.com/blockly/xml'}; used=set()
    def event(instance,name):
        return next(b for b in tree.findall('b:block',ns)
                    if b.get('type')=='component_event'
                    and b.find('b:mutation',ns).get('instance_name')==instance
                    and b.find('b:mutation',ns).get('event_name')==name)
    for instance,name in [('Screen1','Initialize'),('RetryLoadButton','Click')]:
        startup=event(instance,name)
        load=next(b for b in startup.findall('.//b:block',ns)
                  if b.get('type')=='component_method'
                  and b.find('b:mutation',ns).get('method_name')=='LoadModel')
        assert load.find('b:value/b:block/b:field',ns).text=='fruit_classifier.pte'
    failure=event('ExecuTorch1','ErrorOccurred').find('b:statement/b:block',ns)
    condition=failure.find('b:value[@name="IF0"]',ns)
    assert condition.find('.//b:field[@name="TEXT"]',ns).text=='LoadModel'
    load_error=failure.find('b:statement[@name="DO0"]',ns)
    disabled=set()
    for block in load_error.findall('.//b:block[@type="component_set_get"]',ns):
        mutation=block.find('b:mutation',ns)
        if mutation.get('property_name')=='Enabled':
            assert block.find('b:value/b:block/b:field',ns).text=='FALSE'
            disabled.add(mutation.get('instance_name'))
    assert disabled=={'AppleButton','BananaButton','OrangeButton','ChoosePhoto','TakePhotoButton'}
    for block in tree.findall('.//b:block',ns):
        mutation=block.find('b:mutation',ns)
        if not block.get('type','').startswith('component_'): continue
        assert mutation.get('instance_name')=='Screen1' or mutation.get('instance_name') in components
        if mutation.get('component_type')!=api['name']: continue
        if block.get('type')=='component_method':
            name=mutation.get('method_name'); used.add(name)
            assert len(block.findall('b:value',ns))==len(methods[name]['params'])
        if block.get('type')=='component_event': assert mutation.get('event_name') in events
    # Event arguments must be actual parameter names, not the visual 'get' prefix.
    event_parameters={name:{p['name'] for p in event['params']} for name,event in events.items()}
    event_parameters['AfterPicture']={'image'}
    for event_block in tree.findall('b:block',ns):
        mutation=event_block.find('b:mutation',ns)
        if event_block.get('type')!='component_event': continue
        allowed=event_parameters.get(mutation.get('event_name'),set())
        for getter in event_block.findall('.//b:block[@type="lexical_variable_get"]',ns):
            name=getter.find('b:field[@name="VAR"]',ns).text
            assert name in allowed, f'Unbound event argument: {name}'
            assert getter.find('b:mutation/b:eventparam',ns).get('name')==name
    assert used=={'LoadModel','RunImage'}
    for sample in contract['samples']:
        assert z.read('assets/'+sample['file'])==(ROOT/'models/fruit_samples'/sample['file']).read_bytes()
print('PASS: fruit photo predictions, model hash, disjoint dataset splits, attribution, AIA assets and API wiring')
print('Native Android inference, camera and picker behaviour remain unverified.')
