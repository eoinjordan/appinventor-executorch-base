from pathlib import Path
import os, sys, subprocess, urllib.request, zipfile, shutil, io, json, argparse
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
CACHE=ROOT/'.cache'; CACHE.mkdir(exist_ok=True)
BUILD=ROOT/'build'; BUILD.mkdir(exist_ok=True)
JAVA=Path(os.environ.get('JAVA_HOME',r'C:\Program Files\Android\Android Studio\jbr'))/'bin'
SDK=Path(os.environ.get('ANDROID_HOME',str(Path.home()/'AppData/Local/Android/Sdk')))
SEP=os.pathsep
parser=argparse.ArgumentParser(description='Build an App Inventor ExecuTorch extension')
parser.add_argument('--abi',choices=['arm64-v8a','all'],default='arm64-v8a',help='Phone build by default; all adds x86_64 emulator support')
args=parser.parse_args()

def run(*args):
    subprocess.run([str(x) for x in args],check=True)
def artifact(group,name,version,ext):
    target=CACHE/f'{name}-{version}.{ext}'
    if not target.exists():
        candidates=list((Path.home()/'.gradle/caches/modules-2/files-2.1'/group/name/version).glob(f'*/{target.name}'))
        if candidates: shutil.copyfile(candidates[0],target)
        else: urllib.request.urlretrieve(f'https://repo.maven.apache.org/maven2/{group.replace(".","/")}/{name}/{version}/{target.name}',target)
    return target
jars=[]; native={}
for group,name,version,ext in [('org.pytorch','executorch-android','1.5.1','aar'),('com.facebook.fbjni','fbjni','0.7.0','aar'),('com.facebook.soloader','nativeloader','0.10.5','jar'),('org.jetbrains.kotlin','kotlin-stdlib','1.9.23','jar')]:
    p=artifact(group,name,version,ext)
    if ext=='jar': jars.append(p); continue
    with zipfile.ZipFile(p) as z:
        out=CACHE/f'{name}.jar'; out.write_bytes(z.read('classes.jar')); jars.append(out)
        for n in z.namelist():
            if n.startswith(('jni/arm64-v8a/','jni/x86_64/')) and n.endswith('.so'):
                _,abi,fn=n.split('/'); native[(abi,fn)]=z.read(n)
if args.abi != 'all':
    native={key:value for key,value in native.items() if key[0]==args.abi}
classes=BUILD/'classes'; classes.mkdir(exist_ok=True)
android=sorted((SDK/'platforms').glob('*/android.jar'))[0]
deps=ROOT/'lib/appinventor'
if not (deps/'AnnotationProcessors.jar').exists(): run('git','submodule','update','--init','--depth','1')
host_jars=[deps/'json.jar',deps/'AnnotationProcessors.jar',deps/'AndroidRuntime.jar',deps/'kawa.jar',deps/'CommonVersion.jar',deps/'guava.jar',deps/'annotation.jar']
cp=SEP.join(map(str,[android,*[p for p in deps.glob('*.jar') if p.name!='android.jar'],*jars]))
sources=list((ROOT/'src').rglob('*.java'))
run(JAVA/'javac','--release','8','-encoding','UTF-8','-classpath',cp,'-processorpath',SEP.join(map(str,host_jars)),'-processor','com.google.appinventor.components.scripts.ComponentDescriptorGenerator,com.google.appinventor.components.scripts.ComponentListGenerator','-d',classes,*sources)
# Use MIT-generated descriptors; merge dependency bytecode for APK and Companion.
merged=BUILD/'merged.jar'
with zipfile.ZipFile(merged,'w',zipfile.ZIP_DEFLATED) as z:
    names=set()
    for p in classes.rglob('*.class'):
        n=p.relative_to(classes).as_posix(); z.write(p,n); names.add(n)
    for p in jars:
        with zipfile.ZipFile(p) as j:
            for n in j.namelist():
                if n.endswith('.class') and n not in names and n!='module-info.class' and not n.startswith('META-INF/'):
                    z.writestr(n,j.read(n)); names.add(n)
package='org.community.executorch'
stage=BUILD/'aix'/package
if stage.exists(): shutil.rmtree(stage)
(stage/'files').mkdir(parents=True)
components=json.loads((classes/'simple_components.json').read_text())
info=json.loads((classes/'simple_components_build_info.json').read_text())
(stage/'extension.properties').write_text('type=external\n')
(stage/'assets').mkdir(exist_ok=True)
with zipfile.ZipFile(stage/'assets/native-runtime.zip','w',zipfile.ZIP_DEFLATED) as bundle:
    for (abi,fn),data in native.items(): bundle.writestr(abi+'/'+fn,data)
(stage/'components.json').write_text(json.dumps(components))
(stage/'component.json').write_text(json.dumps(components[0]))
# App Inventor uses -v8a/-x8a suffixes in extension native library metadata.
for item in info:
    item['native']=[]
    item['libraries']=[]
    item['assets']=['native-runtime.zip']
    item['androidMinSdk']=['26']
    item['native']=[fn+('-v8a' if abi=='arm64-v8a' else '-x8a') for abi,fn in native if fn=='libc++_shared.so']
(stage/'files/component_build_infos.json').write_text(json.dumps(info))
shutil.copyfile(merged,stage/'files/AndroidRuntime.jar')
for (abi,fn),data in native.items():
    # Only the C++ library is also placed under lib/ to declare supported APK ABIs.
    # NativeRuntime loads the other libraries from the private asset extraction.
    if fn!='libc++_shared.so': continue
    suffix='-v8a' if abi=='arm64-v8a' else '-x8a'
    folder=stage/'files'/abi; folder.mkdir(exist_ok=True)
    (folder/fn).write_bytes(data)
dex=BUILD/'dex'; dex.mkdir(exist_ok=True)
bt=sorted((SDK/'build-tools').iterdir())[-1]
# Run D8 through its main class for a platform-independent Python entry point.
run(JAVA/'java','-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',android,'--output',dex,merged)
with zipfile.ZipFile(stage/'classes.jar','w',zipfile.ZIP_DEFLATED) as z:
    for p in dex.glob('classes*.dex'): z.write(p,p.name)
licenses=ROOT/'licenses'
if licenses.exists():
    for p in licenses.glob('*'): shutil.copyfile(p,stage/'files'/p.name)
out=ROOT/'out'; out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/f'{package}.aix','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in stage.rglob('*'):
        if p.is_file(): z.write(p,p.relative_to(stage.parent).as_posix())
artifact_name='ExecuTorch-ARM64.aix' if args.abi != 'all' else 'ExecuTorch-multi-ABI.aix'
shutil.copyfile(out/f'{package}.aix',out/artifact_name)
print('Built',out/artifact_name, '(bytes:',(out/artifact_name).stat().st_size,')')
