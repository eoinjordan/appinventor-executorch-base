"""Create the beginner fruit photo classifier with all assets and blocks included."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
TYPE='ExecuTorch'
NAME='ExecuTorchFruit'
xml=E.Element('xml',{'xmlns':'https://developers.google.com/blockly/xml'})
contract=json.loads((ROOT/'models/fruit_contract.json').read_text())
components=[]
def component(name,kind,**properties):
    versions={'Label':'5','Button':'7','Image':'4','ImagePicker':'5','Camera':'3','ExecuTorch':'2'}
    components.append({'$Name':name,'$Type':kind,'$Version':versions.get(kind,'1'),'Uuid':str(len(components)+1),**properties})
component('IntroLabel','Label',Text='Apple, banana or orange?',FontSize='22',Width='-2')
component('HelpLabel','Label',Text='Try a sample below, choose a photo, or use the camera. Use one centred fruit on a plain white background. This teaching model knows only these three fruit classes.',Width='-2')
component('FruitImage','Image',Picture='apple.jpg',Height='180',Width='180',ScalePictureToFit='True')
for label in ['apple','banana','orange']:component(label.title()+'Button','Button',Text='Try '+label,Width='-2',Enabled='False')
component('ChoosePhoto','ImagePicker',Text='Choose a fruit photo',Width='-2',Enabled='False')
component('TakePhotoButton','Button',Text='Take a fruit photo',Width='-2',Enabled='False')
component('PredictionLabel','Label',Text='Prediction: waiting for model',FontSize='20',Width='-2')
component('ScoresLabel','Label',Text='Model probability scores will appear here.',Width='-2')
component('StatusLabel','Label',Text='Loading fruit model...',Width='-2')
component('Camera1','Camera')
component('ExecuTorch1',TYPE)
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
def variable(name):b=E.Element('block',{'type':'lexical_variable_get'});field(b,'VAR','get '+name);return b
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


def generic_call(instance,kind,name,args):
    b=E.Element('block',{'type':'component_method'});E.SubElement(b,'mutation',{'component_type':kind,'method_name':name,'is_generic':'false','instance_name':instance});field(b,'COMPONENT_SELECTOR',instance)
    for i,v in enumerate(args):put(b,'ARG'+str(i),v)
    return b
def controls(value):
    return [prop(name,kind,'Enabled',literal(value)) for name,kind in [('AppleButton','Button'),('BananaButton','Button'),('OrangeButton','Button'),('ChoosePhoto','ImagePicker'),('TakePhotoButton','Button')]]
def classify(path):return controls(False)+[prop('StatusLabel','Label','Text',literal('Classifying fruit...')),call('RunImage',[path,literal(32)])]
event('Screen1','Form','Initialize',0,[call('LoadModel',[literal('fruit_classifier.pte')])])
event('ExecuTorch1',TYPE,'ModelLoaded',1,controls(True)+[prop('StatusLabel','Label','Text',literal('Ready. Tap a sample or choose a fruit photo.'))])
for index,label in enumerate(['apple','banana','orange']):
    event(label.title()+'Button','Button','Click',index+2,[prop('FruitImage','Image','Picture',literal(label+'.jpg'))]+classify(literal(label+'.jpg')))
event('ChoosePhoto','ImagePicker','AfterPicking',5,[prop('FruitImage','Image','Picture',prop('ChoosePhoto','ImagePicker','Selection'))]+classify(prop('ChoosePhoto','ImagePicker','Selection')))
event('TakePhotoButton','Button','Click',6,[generic_call('Camera1','Camera','TakePicture',[])])
event('Camera1','Camera','AfterPicture',7,[prop('FruitImage','Image','Picture',variable('image'))]+classify(variable('image')))
result=choose(compare(score(1),score(2)),choose(compare(score(1),score(3)),prediction('apple'),prediction('orange')),choose(compare(score(2),score(3)),prediction('banana'),prediction('orange')))
scores=join([literal('Apple: '),score(1),literal('\nBanana: '),score(2),literal('\nOrange: '),score(3)])
event('ExecuTorch1',TYPE,'InferenceCompleted',8,[result,prop('ScoresLabel','Label','Text',scores),prop('StatusLabel','Label','Text',join([literal('Finished in '),variable('elapsedMs'),literal(' ms. Scores range from 0 to 1. Other objects may be guessed as one of these fruits.')]))]+controls(True))
event('ExecuTorch1',TYPE,'ErrorOccurred',9,[prop('StatusLabel','Label','Text',join([variable('operation'),literal(': '),variable('message')]))]+controls(True))
E.SubElement(xml,'yacodeblocks',{'ya-version':'232','language-version':'36'})
project={'YaVersion':'232','Source':'Form','Properties':{'$Name':'Screen1','$Type':'Form','$Version':'31','Uuid':'0','AppName':NAME,'Title':'Fruit Classifier','Scrollable':'True','Sizing':'Responsive','$Components':components}}
with zipfile.ZipFile(ROOT/'examples'/f'{NAME}.aia','w',zipfile.ZIP_DEFLATED) as z:
    prefix=f'src/appinventor/ai_community/{NAME}/'
    z.writestr(prefix+'Screen1.scm','#|\n$JSON\n'+json.dumps(project)+'\n|#')
    z.writestr(prefix+'Screen1.bky',E.tostring(xml,encoding='unicode'))
    z.writestr('youngandroidproject/project.properties',f'main=appinventor.ai_community.{NAME}.Screen1\nname={NAME}\nassets=../assets\nsource=../src\nbuild=../build\nversioncode=1\nversionname=0.2.0\nuseslocation=False\nactionbar=True\nsizing=Responsive\nshowlistsasjson=True\n')
    for name in ['fruit_classifier.pte','fruit_contract.json']:z.write(ROOT/'models'/name,'assets/'+name)
    for sample in contract['samples']:z.write(ROOT/'models/fruit_samples'/sample['file'],'assets/'+sample['file'])
    z.writestr('assets/FRUIT_ATTRIBUTION.txt',(ROOT/'models/FRUIT_DATASET.md').read_text())
    with zipfile.ZipFile(ROOT/'out/org.community.executorch.aix') as aix:
        for name in aix.namelist():z.writestr('assets/external_comps/'+name,aix.read(name))
print('Created',ROOT/'examples'/f'{NAME}.aia')
