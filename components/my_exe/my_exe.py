#!/usr/bin/env python3
# coding=utf-8
import subprocess, os
import platform

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录


# 执行一个命令，可选阻塞与不阻塞
def my_exe_simple(cmd,wait=0,my_env=None):
    dev = subprocess.Popen(cmd,env=my_env,shell=True,universal_newlines=True,bufsize=1)
    #dev = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=None,universal_newlines=True,bufsize=1)
    if wait == 1:
        dev.wait()

def my_exe_make(cmd,wait=0):
    toolchain_path = current_file_dir
    plat = platform.system().lower()
    if plat == 'windows':
        #print('windows')
        toolchain_path = toolchain_path + '/windows'
    elif plat == 'linux':
        #print('linux')
        toolchain_path = toolchain_path + '/linux'
        
    my_env = {**os.environ, 'PATH': toolchain_path + ';' + os.environ['PATH']}
    my_exe_simple(cmd,wait,my_env)   
    