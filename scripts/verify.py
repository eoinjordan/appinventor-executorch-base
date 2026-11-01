"""Host validation only: input fixtures, AIX descriptors, native ELF and DEX integrity."""
from pathlib import Path
import io
import json
import os
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
os.chdir(root)
java = Path(os.environ.get('JAVA_HOME', r'C:\Program Files\Android\Android Studio\jbr')) / 'bin'
output = root / 'build/tests'
output.mkdir(parents=True, exist_ok=True)
subprocess.run([str(java/'javac'), '--release', '8', '-d', str(output),
               'src/org/community/executorch/TensorData.java', 'tests/TensorDataTest.java'], check=True)
subprocess.run([str(java/'java'), '-cp', str(output), 'TensorDataTest'], check=True)

with zipfile.ZipFile('out/org.community.executorch.aix') as z:
    prefix = 'org.community.executorch/'
    icon_info=json.loads(z.read(prefix+'components.json'))[0]
    assert icon_info['iconName']=='aiwebres/executorch.png'
    assert z.read(prefix+icon_info['iconName']).startswith(b'\x89PNG\r\n\x1a\n')
    assert z.testzip() is None
    descriptor = json.loads(z.read(prefix+'components.json'))[0]
    info = json.loads(z.read(prefix+'files/component_build_infos.json'))[0]
    assert descriptor['androidMinSdk'] == '26'
    assert {m['name'] for m in descriptor['methods']} == {'LoadModel', 'RunModel', 'RunImage', 'UnloadModel'}
    assert {e['name'] for e in descriptor['events']} == {
        'ModelLoaded', 'ModelUnloaded', 'InferenceCompleted', 'ErrorOccurred'}
    assert info['permissions'] == []
    if not any(n.endswith('-x8a') for n in info['native']):
        assert Path('out/org.community.executorch.aix').stat().st_size < 10_000_000, 'Phone archive exceeded upload size budget'
    for name in info['native']:
        suffix = '-v8a' if name.endswith('-v8a') else '-x8a'
        abi = 'arm64-v8a' if suffix == '-v8a' else 'x86_64'
        data = z.read(prefix+'files/'+abi+'/'+name[:-len(suffix)])
        assert data[:4] == b'\x7fELF' and data[4] == 2
    with zipfile.ZipFile(io.BytesIO(z.read(prefix+'classes.jar'))) as dex:
        assert dex.read('classes.dex').startswith(b'dex\n')
    with zipfile.ZipFile(io.BytesIO(z.read(prefix+'assets/native-runtime.zip'))) as libs:
        assert len(libs.namelist()) in (3, 6)
        assert {n.split("/")[0] for n in libs.namelist()} >= {"arm64-v8a"}
    assert z.read(prefix+'extension.properties').decode().splitlines() == ['type=external']
print('PASS: minimal block API, zero permissions, minSDK, native assets and DEX packaging')

example = Path('examples/ExecuTorchSmoke.aia')
if example.exists():
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(example) as z:
        block_file = next(n for n in z.namelist() if n.endswith('.bky'))
        ET.fromstring(z.read(block_file))
        assert z.read('assets/add_one.pte') == Path('models/add_one.pte').read_bytes()
    print('PASS: example archive and block XML (App Inventor import remains unverified)')
