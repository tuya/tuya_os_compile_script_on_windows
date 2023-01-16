#!/usr/bin/env python3
# coding=utf-8
import subprocess, os, sys
import platform
import tkinter
from tkinter import Label, Button, filedialog

my_exe_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(my_exe_file_dir+'/../components')
from my_string.my_string import my_string_replace_with_dict


# 执行一个命令，可选阻塞与不阻塞
def my_exe_simple(cmd,wait=0,my_env=None,var_map=None):
    if var_map != None:
        cmd = my_string_replace_with_dict(cmd,var_map)
        if my_env != None:
            my_env = my_string_replace_with_dict(my_env,var_map)
           
    if my_env != None:
        my_env = my_exe_add_env_path(my_env)
     
    #print('[cmd]:',cmd[:1000])
    dev = subprocess.Popen(cmd,env=my_env,shell=True,universal_newlines=True,bufsize=1)
    #dev = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=None,universal_newlines=True,bufsize=1)
    if wait == 1:
        dev.wait()

def my_exe_make(cmd,wait=0):
    toolchain_path = my_exe_file_dir
    toolchain_path = toolchain_path + '/' + my_exe_get_system_kind()
        
    my_exe_simple(cmd,wait,toolchain_path)   
    
def my_exe_get_system_kind():
    return platform.system().lower()

def my_exe_add_env_path(PATH):
    # https://blog.51cto.com/alsww/1787848
    if isinstance(PATH,dict):
        return {**os.environ,**PATH} 
    else:
        if my_exe_get_system_kind() == 'windows':
            return {**os.environ, 'PATH': PATH + ';' + os.environ['PATH']}
        else:
            return {**os.environ, 'PATH': PATH + ':' + os.environ['PATH']}

def __my_exe_check_version(file,strlist):
    ret = {}
    with open(file,'r') as fp:
        contents = fp.read()
        for str in strlist:
            ret[str] = (len(contents) - len(contents.replace(str,''))) // len(str)
        fp.close()
    return ret
    
def my_exe_get_install_path(NAME):
    EXE_TOOL = {
        '$KEIL_PATH':{
           'PATH':'C:/Keil_v5',
           'KEY':'UV4',
           'FATHER':1,
           'TITLE':'请选择 Keil 的可执行文件 "UV4.exe"'
        },
        '$CDK_PATH':{
           'PATH':'D:/C-Sky/CDK',
           'KEY':'CDK',
           'FATHER':0,
           'TITLE':'请选择 Keil 的可执行文件 "cdk.exe"'
        },
        '$KEIL4_PATH':{
           'PATH':'D:/keil 4',
           'KEY':'UV4',
           'FATHER':1,
           'TITLE':'请选择 Keil4 的可执行文件 "UV4.exe"'
        },
        '$IAR840_PATH':{
           'PATH':'D:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3/common/bin',
           'KEY':'ARM 8.40',
           'FATHER':0,
           'TITLE':'请选择 IAR 的可执行文件 "IarBuild.exe"'
        },
        '$IAR930_PATH':{
           'PATH':'D:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3/common/bin',
           'KEY':'ARM 9.30',
           'FATHER':0,
           'TITLE':'请选择 IAR 的可执行文件 "IarBuild.exe"'
        },
        '$CODEBLOCKS_PATH':{
           'PATH':'C:/Program Files (x86)/CodeBlocks',
           'KEY':'CodeBlocks',
           'FATHER':0,
           'TITLE':'请选择 CodeBlocks 的可执行文件 "codeblocks.exe"'
        },
        #,
        #'$CMSIS_VER':{
        #   'PATH':'C:/Keil_v5',
        #   'KEY':'UV4',
        #   'FATHER':1,
        #   'TITLE':'请选择 Keil 的可执行文件 "UV4.exe"'
        #}
    }
    
    # Get the keil path
    EXE_PATH=EXE_TOOL[NAME]['PATH']
    if not os.path.exists(EXE_PATH):
        evns = os.environ.get("TUYAOS_COMPILE_TOOL")
        if None != evns:
            for evn in evns.split(';'):
                if EXE_TOOL[NAME]['KEY'] in evn:
                    PATH = os.path.abspath(os.path.join(evn,'../'*EXE_TOOL[NAME]['FATHER'])).replace('\\','/')
                
                    OK = True
                    if NAME == '$KEIL4_PATH':
                        ret = __my_exe_check_version(PATH + '/TOOLS.INI',['VERSION=4.'])
                        if ret['VERSION=4.'] == 0:
                            OK = False
                    elif NAME == '$KEIL4_PATH':
                        ret = __my_exe_check_version(PATH + '/TOOLS.INI',['VERSION=5.'])
                        if ret['VERSION=5.'] == 0:
                            OK = False
                            
                    if OK:
                        EXE_PATH = PATH
                        break
                    
    if not os.path.exists(EXE_PATH):
        TITLE = EXE_TOOL[NAME]['TITLE']
        window = tkinter.Tk()
        window.title(TITLE)
        window.geometry('400x200')
        
        #var = tkinter.StringVar()
        #label1 = Label(window, bg='#fe4b03', fg='#FFFFFF', height=0, width=90, textvariable = var)
        #var.set(TITLE)
        label1 = Label(window, text=TITLE, bg='#fe4b03', fg='#FFFFFF', height=0, width=90)
        label1.pack()

        evn = filedialog.askopenfilename(title=TITLE, filetypes=[('EXE', '*.exe'), ('All Files', '*')])
        evn = os.path.dirname(evn) 
        
        label2 = Label(window, text='为了方便，请将: '+evn+'\n加入到: TUYAOS_COMPILE_TOOL 环境变量中\n修改环境变量后可能需要重启电脑才会生效！', bg='blue', fg='#FFFFFF', height=0, width=90)
        label2.pack()
        
        btn = Button(window,text='OK',width=15,height=0,command=window.destroy)
        btn.pack(side = 'bottom')
        
        window.mainloop()
      
        EXE_PATH = os.path.abspath(os.path.join(evn,'../'*EXE_TOOL[NAME]['FATHER'])).replace('\\','/')
        
    # 附属变量获取
    # 1. $CMSIS_PATH -- 是先从环境变量中获取 KEIL_PATH，然后计算 CMSIS_PATH
    # if NAME == '$CMSIS_PATH':
    #    EXE_PATH += '/ARM/PACK/ARM/CMSIS'
    #    for root, dirs, files in os.walk(EXE_PATH):
    #        if len(dirs) > 0:
    #            dirs.sort(reverse = True)
    #            EXE_PATH += ('/'+dirs[0])
    #        break
    
    return EXE_PATH
