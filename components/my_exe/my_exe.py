#!/usr/bin/env python3
# coding=utf-8
import subprocess, os, sys
import platform
import tkinter
from tkinter import Label, Button, filedialog

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/../components')
from my_string.my_string import my_string_replace_with_dict


# 执行一个命令，可选阻塞与不阻塞
def my_exe_simple(cmd,wait=0,my_env=None,var_map=None):
    if var_map != None:
        cmd = my_string_replace_with_dict(cmd,var_map)
        if my_env != None:
            my_env = my_string_replace_with_dict(my_env,var_map)
            my_env = my_exe_add_env_path(my_env)
    
    dev = subprocess.Popen(cmd,env=my_env,shell=True,universal_newlines=True,bufsize=1)
    #dev = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=None,universal_newlines=True,bufsize=1)
    if wait == 1:
        dev.wait()

def my_exe_make(cmd,wait=0):
    toolchain_path = current_file_dir
    toolchain_path = toolchain_path + '/' + my_exe_get_system_kind()
        
    my_env = my_exe_add_env_path(toolchain_path)
    my_exe_simple(cmd,wait,my_env)   
    
def my_exe_get_system_kind():
    return platform.system().lower()

def my_exe_add_env_path(PATH):
    if my_exe_get_system_kind() == 'windows':
        return {**os.environ, 'PATH': PATH + ';' + os.environ['PATH']}
    else:
        return {**os.environ, 'PATH': PATH + ':' + os.environ['PATH']}

def my_exe_get_install_path(NAME):
    EXE_TOOL = {
        '$KEIL_PATH':{
           'PATH':'C:/Keil_v5',
           'KEY':'UV4',
           'FATHER':1,
           'TITLE':'请选择 Keil 的可执行文件 "UV4.exe"'
        }
    }
    
    # Get the keil path
    EXE_PATH=EXE_TOOL[NAME]['PATH']
    if not os.path.exists(EXE_PATH):
        for evn in os.environ.get("TUYAOS_COMPILE_TOOL").split(';'):
            if EXE_TOOL[NAME]['KEY'] in evn:
                EXE_PATH = os.path.abspath(os.path.join(evn,'../'*EXE_TOOL[NAME]['FATHER'])).replace('\\','/')
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
        
    return EXE_PATH