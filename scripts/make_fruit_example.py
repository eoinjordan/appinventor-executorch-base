"""Create the beginner fruit photo classifier with all assets and blocks included."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
TYPE='ExecuTorch'
NAME='ExecuTorchFruit'
xml=E.Element('xml',{'xmlns':'https://developers.google.com/blockly/xml'})
contract=json.loads((ROOT/'models/fruit_contract.json').read_text())
components=[]
def component(name,kind,parent=None,**properties):
    versions={'Label':'5','Button':'7','Image':'4','ImagePicker':'5','Camera':'3','ExecuTorch':'2','VerticalArrangement':'4','HorizontalArrangement':'4','ActivityStarter':'6'}
    item={'$Name':name,'$Type':kind,'$Version':versions.get(kind,'1'),'Uuid':str(component.counter),**properties}
    component.counter+=1
    (components if parent is None else parent.setdefault('$Components',[])).append(item)
    return item
component.counter=1
INK='&HFF18352B'
MUTED='&HFF586A62'
GREEN='&HFF246747'
WHITE='&HFFFFFFFF'
body=component('Content','VerticalArrangement',Width='-1092',AlignHorizontal='3')
def gap(name,height=10,parent=body):
    component(name,'Label',parent=parent,Text='',Height=str(height),Width='-2')
gap('TopSpace',12)
component('IntroLabel','Label',parent=body,Text='Meet your fruit.',FontSize='24',FontBold='True',TextColor=INK,Width='-2')
component('SubtitleLabel','Label',parent=body,Text='Apple, banana or orange? Try it on your phone.',FontSize='14',TextColor=MUTED,Width='-2')
gap('ImageSpace',8)
preview=component('Preview','VerticalArrangement',parent=body,Width='-2',Height='152',BackgroundColor=WHITE,AlignHorizontal='3',AlignVertical='2')
component('FruitImage','Image',parent=preview,Picture='apple.jpg',Height='140',Width='140',ScalePictureToFit='True')
gap('SampleSpace',8)
component('SamplesLabel','Label',parent=body,Text='SAMPLE PHOTOS',FontSize='11',FontBold='True',TextColor=MUTED,Width='-2')
samples=component('SampleButtons','HorizontalArrangement',parent=body,Width='-2',AlignHorizontal='3')
for label in ['apple','banana','orange']:
    component(label.title()+'Button','Button',parent=samples,Text=label.title(),Width='-1030',Height='44',FontSize='14',TextColor=INK,BackgroundColor='&HFFE2EEE5',Shape='1',Enabled='False')
gap('PhotoSpace',8)
photos=component('PhotoButtons','HorizontalArrangement',parent=body,Width='-2',AlignHorizontal='3')
component('ChoosePhoto','ImagePicker',parent=photos,Text='Choose photo',Width='-1045',Height='48',FontSize='14',BackgroundColor=GREEN,TextColor=WHITE,Shape='1',Enabled='False')
component('TakePhotoButton','Button',parent=photos,Text='Take photo',Width='-1045',Height='48',FontSize='14',BackgroundColor=GREEN,TextColor=WHITE,Shape='1',Enabled='False')
gap('ResultSpace',10)
result_panel=component('ResultPanel','VerticalArrangement',parent=body,Width='-2',BackgroundColor=WHITE)
component('PredictionLabel','Label',parent=result_panel,Text='Your result appears here',FontSize='20',FontBold='True',TextColor=INK,Width='-2')
component('ScoresLabel','Label',parent=result_panel,Text='Select a sample or add your own photo.',FontSize='13',TextColor=MUTED,Width='-2')
component('StatusLabel','Label',parent=body,Text='Loading fruit model...',FontSize='12',TextColor=MUTED,Width='-2')
component('LoadErrorLabel','Label',parent=body,Text='',FontSize='13',TextColor='&HFFB3261E',Width='-2')
component('RetryLoadButton','Button',parent=body,Text='Retry loading fruit model',Visible='False',Width='-2',Height='48')
gap('HelpSpace',8)
component('HelpLabel','Label',parent=body,Text='Best with one centred fruit on a plain white background. This demo knows only apple, banana and orange; other objects may be guessed as one of them.',FontSize='12',TextColor=MUTED,Width='-2')
gap('LearnSpace',8)
component('LocalAILabel','Label',parent=body,Text="This is a local AI machine learning model. It uses your phone's processor to run a PyTorch ExecuTorch model. Your photos are processed on your phone. To learn more about AI or PyTorch, tap a link below.",FontSize='13',TextColor=INK,Width='-2')
component('LearnLabel','Label',parent=body,Text='LEARN MORE',FontSize='11',FontBold='True',TextColor=MUTED,Width='-2')
learning=component('LearningLinks','HorizontalArrangement',parent=body,Width='-2',AlignHorizontal='3')
LEARNING_LINKS=[
    ('LearnMLButton','MLDocs','Learn about AI','https://docs.pytorch.org/tutorials/beginner/basics/intro.html'),
    ('ExecuTorchDocsButton','ExecuTorchDocs','PyTorch / ExecuTorch','https://docs.pytorch.org/executorch/stable/index.html'),
]
for button,starter,title,url in LEARNING_LINKS:
    component(button,'Button',parent=learning,Text=title,Width='-1045',Height='48',FontSize='13',TextColor=GREEN,BackgroundColor=WHITE,Shape='1')
    component(starter,'ActivityStarter',Action='android.intent.action.VIEW',DataUri=url)
gap('BottomSpace',12)
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


def generic_call(instance,kind,name,args):
    b=E.Element('block',{'type':'component_method'});E.SubElement(b,'mutation',{'component_type':kind,'method_name':name,'is_generic':'false','instance_name':instance});field(b,'COMPONENT_SELECTOR',instance)
    for i,v in enumerate(args):put(b,'ARG'+str(i),v)
    return b
def controls(value):
    return [prop(name,kind,'Enabled',literal(value)) for name,kind in [('AppleButton','Button'),('BananaButton','Button'),('OrangeButton','Button'),('ChoosePhoto','ImagePicker'),('TakePhotoButton','Button')]]
def classify(path):return controls(False)+[prop('StatusLabel','Label','Text',literal('Classifying fruit...')),call('RunImage',[path,literal(32)])]
def load_model():
    return controls(False)+[prop('RetryLoadButton','Button','Visible',literal(False)),prop('StatusLabel','Label','Text',literal('Loading bundled fruit model...')),call('LoadModel',[literal('fruit_classifier.pte')])]

event('Screen1','Form','Initialize',0,load_model())
event('ExecuTorch1',TYPE,'ModelLoaded',1,controls(True)+[prop('LoadErrorLabel','Label','Text',literal('')),prop('RetryLoadButton','Button','Visible',literal(False)),prop('StatusLabel','Label','Text',literal('Ready · Works offline'))])
for index,label in enumerate(['apple','banana','orange']):
    event(label.title()+'Button','Button','Click',index+2,[prop('FruitImage','Image','Picture',literal(label+'.jpg'))]+classify(literal(label+'.jpg')))
event('ChoosePhoto','ImagePicker','AfterPicking',5,[prop('FruitImage','Image','Picture',prop('ChoosePhoto','ImagePicker','Selection'))]+classify(prop('ChoosePhoto','ImagePicker','Selection')))
event('TakePhotoButton','Button','Click',6,[generic_call('Camera1','Camera','TakePicture',[])])
event('Camera1','Camera','AfterPicture',7,[prop('FruitImage','Image','Picture',variable('image'))]+classify(variable('image')))
result=choose(compare(score(1),score(2)),choose(compare(score(1),score(3)),prediction('apple'),prediction('orange')),choose(compare(score(2),score(3)),prediction('banana'),prediction('orange')))
scores=join([literal('Apple: '),score(1),literal('\nBanana: '),score(2),literal('\nOrange: '),score(3)])
event('ExecuTorch1',TYPE,'InferenceCompleted',8,[result,prop('ScoresLabel','Label','Text',scores),prop('StatusLabel','Label','Text',join([literal('Finished in '),variable('elapsedMs'),literal(' ms · On your device')]))]+controls(True))
load_failed=E.Element('block',{'type':'logic_compare'});field(load_failed,'OP','EQ');put(load_failed,'A',variable('operation'));put(load_failed,'B',literal('LoadModel'))
error_branch=E.Element('block',{'type':'controls_if'});E.SubElement(error_branch,'mutation',{'else':'1'});put(error_branch,'IF0',load_failed)
statement(error_branch,'DO0',controls(False)+[
    prop('LoadErrorLabel','Label','Text',join([literal('Could not load bundled fruit_classifier.pte: '),variable('message')])),
    prop('StatusLabel','Label','Text',literal('Model unavailable. Retry loading before choosing a photo.')),
    prop('RetryLoadButton','Button','Visible',literal(True)),
])
statement(error_branch,'ELSE',[prop('StatusLabel','Label','Text',join([variable('operation'),literal(': '),variable('message')]))]+controls(True))
event('ExecuTorch1',TYPE,'ErrorOccurred',9,[error_branch])
event('RetryLoadButton','Button','Click',12,load_model())
for index,(button,starter,title,url) in enumerate(LEARNING_LINKS,10):
    event(button,'Button','Click',index,[generic_call(starter,'ActivityStarter','StartActivity',[])])
E.SubElement(xml,'yacodeblocks',{'ya-version':'232','language-version':'36'})
project={'YaVersion':'232','Source':'Form','Properties':{'$Name':'Screen1','$Type':'Form','$Version':'31','Uuid':'0','AppName':NAME,'Title':'Fruit Classifier','Scrollable':'True','Sizing':'Responsive','AlignHorizontal':'3','BackgroundColor':'&HFFF3F6F2','PrimaryColor':GREEN,'PrimaryColorDark':'&HFF183F2D','AccentColor':GREEN,'$Components':components}}
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
