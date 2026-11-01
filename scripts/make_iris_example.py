"""Build the beginner Iris AIA with the current bundled extension."""
from pathlib import Path
import json
import zipfile
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
TYPE='ExecuTorch'
NAME='ExecuTorchIris'
NS='https://developers.google.com/blockly/xml'
xml=E.Element('xml',{'xmlns':NS})
contract=json.loads((ROOT/'models/iris_contract.json').read_text(encoding='utf-8'))
components=[]
with zipfile.ZipFile(ROOT/'out/org.community.executorch.aix') as aix:
    extension_version=str(json.loads(aix.read('org.community.executorch/components.json'))[0]['version'])
def component(name,kind,**properties):
    versions={'Label':'5','Button':'7','TextBox':'6','ExecuTorch':extension_version}
    item={'$Name':name,'$Type':kind,'$Version':versions.get(kind,'1'),'Uuid':str(len(components)+1),**properties}
    components.append(item)
component('IntroLabel','Label',Text='Iris flower classifier\nEnter four measurements in centimetres, or choose a preset. Tap Classify to predict the species. This is a learning demo.',FontSize='18',Width='-2')
fields=['SepalLength','SepalWidth','PetalLength','PetalWidth']
for field,title,value in zip(fields,contract['features'],contract['presets'][0]['values']):
    component(field+'Label','Label',Text=title)
    component(field,'TextBox',Text=str(value),Hint=title,NumbersOnly='True',Width='-2')
for preset in contract['presets']:
    component(preset['label'].title()+'Button','Button',Text='Try '+preset['label'],Width='-2')
component('ClassifyButton','Button',Text='Classify flower',Enabled='False',Width='-2')
component('StatusLabel','Label',Text='Loading model...',Width='-2')
component('PredictionLabel','Label',Text='Prediction: waiting',FontSize='20',Width='-2')
component('ScoresLabel','Label',Text='Scores will appear here.',Width='-2')
component('ExecuTorch1',TYPE)
properties={'$Name':'Screen1','$Type':'Form','$Version':'31','Uuid':'0','AppName':NAME,'Title':'Iris Flower Classifier','Scrollable':'True','Sizing':'Responsive','$Components':components}
project={'YaVersion':'232','Source':'Form','Properties':properties}
def field(b,n,v):E.SubElement(b,'field',{'name':n}).text=str(v)
def literal(value):
    if isinstance(value,bool):
        b=E.Element('block',{'type':'logic_boolean'});field(b,'BOOL','TRUE' if value else 'FALSE')
    elif isinstance(value,str):
        b=E.Element('block',{'type':'text'});field(b,'TEXT',value)
    elif isinstance(value,list):
        b=E.Element('block',{'type':'lists_create_with'});E.SubElement(b,'mutation',{'items':str(len(value))})
        for i,v in enumerate(value):put(b,'ADD'+str(i),literal(v))
    else:
        b=E.Element('block',{'type':'math_number'});field(b,'NUM',value)
    return b
def put(b,n,value):E.SubElement(b,'value',{'name':n}).append(value)
def prop(instance,kind,name,value=None):
    b=E.Element('block',{'type':'component_set_get'})
    E.SubElement(b,'mutation',{'component_type':kind,'set_or_get':'get' if value is None else 'set','property_name':name,'is_generic':'false','instance_name':instance})
    field(b,'COMPONENT_SELECTOR',instance);field(b,'PROP',name)
    if value is not None:put(b,'VALUE',value)
    return b
def call(name,args):
    b=E.Element('block',{'type':'component_method'})
    E.SubElement(b,'mutation',{'component_type':TYPE,'method_name':name,'is_generic':'false','instance_name':'ExecuTorch1'});field(b,'COMPONENT_SELECTOR','ExecuTorch1')
    for i,v in enumerate(args):put(b,'ARG'+str(i),v)
    return b
def chain(blocks):
    first=blocks[0];current=first
    for b in blocks[1:]:E.SubElement(current,'next').append(b);current=b
    return first
def statement(parent,name,blocks):E.SubElement(parent,'statement',{'name':name}).append(chain(blocks))
def event(instance,kind,name,index,blocks):
    b=E.SubElement(xml,'block',{'type':'component_event','x':str(30+(index%2)*650),'y':str(30+(index//2)*320)})
    E.SubElement(b,'mutation',{'component_type':kind,'is_generic':'false','instance_name':instance,'event_name':name});field(b,'COMPONENT_SELECTOR',instance)
    statement(b,'DO',blocks)
def variable(name):
    b=E.Element('block',{'type':'lexical_variable_get'})
    E.SubElement(E.SubElement(b,'mutation'),'eventparam',{'name':name})
    field(b,'VAR',name)
    return b
def join(values):
    b=E.Element('block',{'type':'text_join'});E.SubElement(b,'mutation',{'items':str(len(values))})
    for i,v in enumerate(values):put(b,'ADD'+str(i),v)
    return b
def score(i):
    b=E.Element('block',{'type':'lists_select_item'});put(b,'LIST',variable('values'));put(b,'NUM',literal(i));return b
def compare(a,b):
    block=E.Element('block',{'type':'math_compare'});field(block,'OP','GTE');put(block,'A',a);put(block,'B',b);return block
def prediction(label):return prop('PredictionLabel','Label','Text',literal('Prediction: '+label))
def choose(condition,yes,no):
    b=E.Element('block',{'type':'controls_if'});E.SubElement(b,'mutation',{'else':'1'});put(b,'IF0',condition);statement(b,'DO0',[yes]);statement(b,'ELSE',[no]);return b

event('Screen1','Form','Initialize',0,[call('LoadModel',[literal('iris_classifier.pte')])])
event('ExecuTorch1',TYPE,'ModelLoaded',1,[prop('StatusLabel','Label','Text',literal('Ready. Choose a preset or enter measurements, then tap Classify.')),prop('ClassifyButton','Button','Enabled',literal(True))])
for i,preset in enumerate(contract['presets']):
    blocks=[prop(f,'TextBox','Text',literal(str(v))) for f,v in zip(fields,preset['values'])]
    blocks.append(prop('StatusLabel','Label','Text',literal('Preset: '+preset['label']+'. Tap Classify.')))
    event(preset['label'].title()+'Button','Button','Click',i+2,blocks)
input_list=E.Element('block',{'type':'lists_create_with'});E.SubElement(input_list,'mutation',{'items':'4'})
for i,f in enumerate(fields):put(input_list,'ADD'+str(i),prop(f,'TextBox','Text'))
event('ClassifyButton','Button','Click',5,[prop('ClassifyButton','Button','Enabled',literal(False)),prop('StatusLabel','Label','Text',literal('Running on-device model...')),call('RunModel',[input_list,literal([1,4])])])
result=choose(compare(score(1),score(2)),choose(compare(score(1),score(3)),prediction('setosa'),prediction('virginica')),choose(compare(score(2),score(3)),prediction('versicolor'),prediction('virginica')))
scores=join([literal('Setosa: '),score(1),literal('\nVersicolor: '),score(2),literal('\nVirginica: '),score(3)])
event('ExecuTorch1',TYPE,'InferenceCompleted',6,[result,prop('ScoresLabel','Label','Text',scores),prop('StatusLabel','Label','Text',join([literal('Finished in '),variable('elapsedMs'),literal(' ms. Scores are probabilities from 0 to 1.')])),prop('ClassifyButton','Button','Enabled',literal(True))])
can_retry=E.Element('block',{'type':'logic_compare'});field(can_retry,'OP','NEQ');put(can_retry,'A',variable('operation'));put(can_retry,'B',literal('LoadModel'))
event('ExecuTorch1',TYPE,'ErrorOccurred',7,[prop('StatusLabel','Label','Text',join([variable('operation'),literal(': '),variable('message')])),prop('ClassifyButton','Button','Enabled',can_retry)])
E.SubElement(xml,'yacodeblocks',{'ya-version':'232','language-version':'36'})
out=ROOT/'examples'/f'{NAME}.aia'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    path=f'src/appinventor/ai_community/{NAME}/'
    z.writestr(path+'Screen1.scm','#|\n$JSON\n'+json.dumps(project)+'\n|#')
    z.writestr(path+'Screen1.bky',E.tostring(xml,encoding='unicode'))
    z.writestr('youngandroidproject/project.properties',f'main=appinventor.ai_community.{NAME}.Screen1\nname={NAME}\nassets=../assets\nsource=../src\nbuild=../build\nversioncode=1\nversionname=0.1.0\nuseslocation=False\nactionbar=True\nsizing=Responsive\nshowlistsasjson=True\n')
    for file in ['iris_classifier.pte','iris_contract.json']:z.write(ROOT/'models'/file,'assets/'+file)
    z.writestr('assets/IRIS_ATTRIBUTION.txt','Fisher, R. (1936). Iris [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C56C76 . CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Model trained on the scikit-learn copy; parameters transformed into a classifier.\n')
    with zipfile.ZipFile(ROOT/'out/org.community.executorch.aix') as aix:
        for name in aix.namelist():z.writestr('assets/external_comps/'+name,aix.read(name))
print('Created',out)
