"""Generate an importable App Inventor project with actual component blocks."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
T='ExecuTorch'
project={'YaVersion':'232','Source':'Form','Properties':{'$Name':'Screen1','$Type':'Form','$Version':'31','Uuid':'0','AppName':'ExecuTorchSmoke','Title':'ExecuTorch Smoke Test','$Components':[{'$Name':'RunButton','$Type':'Button','$Version':'7','Uuid':'1','Text':'Load model and run [1,2,3,4] + 1'},{'$Name':'ResultLabel','$Type':'Label','$Version':'5','Uuid':'2','Text':'Expected: [2,3,4,5]'},{'$Name':'ExecuTorch1','$Type':T,'$Version':'3','Uuid':'3'}]}}
xml=ET.Element('xml',{'xmlns':'https://developers.google.com/blockly/xml'})
def field(b,name,value): ET.SubElement(b,'field',{'name':name}).text=str(value)
def literal(value):
    if isinstance(value,str): b=ET.Element('block',{'type':'text'});field(b,'TEXT',value)
    elif isinstance(value,list):
        b=ET.Element('block',{'type':'lists_create_with'});ET.SubElement(b,'mutation',{'items':str(len(value))})
        for i,v in enumerate(value): ET.SubElement(b,'value',{'name':'ADD'+str(i)}).append(literal(v))
    else: b=ET.Element('block',{'type':'math_number'});field(b,'NUM',value)
    return b
def call(method,args):
    b=ET.Element('block',{'type':'component_method'});ET.SubElement(b,'mutation',{'component_type':T,'method_name':method,'is_generic':'false','instance_name':'ExecuTorch1'});field(b,'COMPONENT_SELECTOR','ExecuTorch1')
    for i,a in enumerate(args): ET.SubElement(b,'value',{'name':'ARG'+str(i)}).append(literal(a))
    return b
def event(component,ctype,name,x,y):
    b=ET.SubElement(xml,'block',{'type':'component_event','x':str(x),'y':str(y)});ET.SubElement(b,'mutation',{'component_type':ctype,'is_generic':'false','instance_name':component,'event_name':name});field(b,'COMPONENT_SELECTOR',component);return b
def label(block,param):
    setb=ET.SubElement(ET.SubElement(block,'statement',{'name':'DO'}),'block',{'type':'component_set_get'});ET.SubElement(setb,'mutation',{'component_type':'Label','set_or_get':'set','property_name':'Text','is_generic':'false','instance_name':'ResultLabel'});field(setb,'COMPONENT_SELECTOR','ResultLabel');field(setb,'PROP','Text');get=ET.SubElement(ET.SubElement(setb,'value',{'name':'VALUE'}),'block',{'type':'lexical_variable_get'});ET.SubElement(ET.SubElement(get,'mutation'),'eventparam',{'name':param});field(get,'VAR',param)
b=event('RunButton','Button','Click',20,20);ET.SubElement(b,'statement',{'name':'DO'}).append(call('LoadModel',['add_one.pte']))
b=event('ExecuTorch1',T,'ModelLoaded',20,220);ET.SubElement(b,'statement',{'name':'DO'}).append(call('RunModel',[[1,2,3,4],[1,4]]))
label(event('ExecuTorch1',T,'InferenceCompleted',20,430),'values')
label(event('ExecuTorch1',T,'ErrorOccurred',20,630),'message')
ET.SubElement(xml,'yacodeblocks',{'ya-version':'232','language-version':'36'})
with zipfile.ZipFile(root/'examples/ExecuTorchSmoke.aia','w',zipfile.ZIP_DEFLATED) as z:
    path='src/appinventor/ai_community/ExecuTorchSmoke/'
    z.writestr(path+'Screen1.scm','#|\n$JSON\n'+json.dumps(project)+'\n|#')
    z.writestr(path+'Screen1.bky',ET.tostring(xml,encoding='unicode'))
    z.writestr('youngandroidproject/project.properties','main=appinventor.ai_community.ExecuTorchSmoke.Screen1\nname=ExecuTorchSmoke\nassets=../assets\nsource=../src\nbuild=../build\nversioncode=1\nversionname=0.1.0\nuseslocation=False\nactionbar=True\nsizing=Responsive\nshowlistsasjson=True\n')
    z.write(root/'models/add_one.pte','assets/add_one.pte')
    with zipfile.ZipFile(root/'out/org.community.executorch.aix') as aix:
        for name in aix.namelist(): z.writestr('assets/external_comps/'+name,aix.read(name))
print('Created examples/ExecuTorchSmoke.aia (import and phone execution still need verification)')
