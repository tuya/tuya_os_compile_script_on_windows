#!/usr/bin/env python3
# coding=utf-8
import subprocess, os, sys
import json
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


  
def my_exe_get_install_path(NAME):
    def __my_exe_check_version(file,strlist):
        ret = {}
        with open(file,'r') as fp:
            contents = fp.read()
            for str in strlist:
                ret[str] = (len(contents) - len(contents.replace(str,''))) // len(str)
            fp.close()
        return ret
              
    # 读取 json_file 返回字典
    def __my_exe_read_json(json_file):
        if os.path.exists(json_file) == False:
            return {}

        with open(json_file,'r',encoding='utf-8') as fp:
            c = json.load(fp)
            fp.close()
            return c

    # 将 json_root 字典，保存为 json 文件
    def __my_exe_save_json(json_file, json_root):
        with open(json_file,'w',encoding='utf-8') as fp2:
            fp2.write(json.dumps(json_root, sort_keys=False, indent=4, separators=(',', ': '),ensure_ascii=False))
            fp2.close()
    
    EXE_TOOL = __my_exe_read_json(my_exe_file_dir+'/my_exe.json')

    # 从环境变量中获取对应 IDE 的环境变量
    # 1）判断默认的 PATH 是否存在，如果存在，则直接使用，不做任何进一步判断
    # 2）使用 KEY 值匹配 TUYAOS_COMPILE_TOOL 环境变量中的所有环境变量，一旦匹配，则认为该环境变量为所需 PATH (KEY，是数组类型，支持个可能的关键词)
    # 3）弹出窗口，让用户自己选择安装的路径，我们通过判断是否是需要的 EXE，如果用户选错了，就退出；如果用户选对了，就将该路径保存在 my_exe.json 的 PATH 中
    EXE_PATH=EXE_TOOL[NAME]['PATH']
    if not os.path.exists(EXE_PATH):
        evns = os.environ.get("TUYAOS_COMPILE_TOOL")
        if None != evns:
            for evn in evns.split(';'):
                OK = False
                for key in EXE_TOOL[NAME]['KEY']:
                    if key in evn:
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
                if OK:
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

        exe_file = filedialog.askopenfilename(title=TITLE, filetypes=[('EXE', '*.exe'), ('All Files', '*')])
        exe_path = os.path.dirname(exe_file) 
        exe_name = os.path.basename(exe_file)

        ok = 1
        if EXE_TOOL[NAME]['EXE'].lower() == exe_name.lower(): 
            ok = 1
            label2 = Label(window, text='为了方便，请将: '+exe_path+'\n加入到: TUYAOS_COMPILE_TOOL 环境变量中\n修改环境变量后可能需要重启电脑才会生效！', bg='blue', fg='#FFFFFF', height=0, width=90)
            label2.pack()
        else:
            ok = 0
            label2 = Label(window, text='请确保选择到了:'+EXE_TOOL[NAME]['EXE'], bg='blue', fg='#FFFFFF', height=0, width=90)
            label2.pack()

        btn = Button(window,text='OK',width=15,height=0,command=window.destroy)
        btn.pack(side = 'bottom')
        window.mainloop()
        
        if ok:
            EXE_PATH = os.path.abspath(os.path.join(exe_path,'../'*EXE_TOOL[NAME]['FATHER'])).replace('\\','/')
            
            # 用户自己输入的可执行文件路径，直接修改 my_exe.json 中的默认搜索路径，这样可以用户不配置环境变量情况下，只用选一次
            EXE_TOOL[NAME]['PATH'] = EXE_PATH 
            __my_exe_save_json(my_exe_file_dir+'/my_exe.json',EXE_TOOL)
        else:
            print('ERROR:指定 IDE 路径错误!!!')
            exit(0)

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
