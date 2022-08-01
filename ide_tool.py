#!/usr/bin/env python
# coding=utf-8
import sys
import os
import json

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
if current_file_dir == '':
    current_file_dir = '.'
sys.path.append(current_file_dir+'/components')
from my_depend.my_depend import my_depend
depend = my_depend()
depend.check()

from my_template.my_template import my_template
from my_kconfig.my_kconfig import my_kconfig
from my_ide.my_ide_gcc import *
from my_ide.my_ide_keil import *
from my_ide.my_ide_cdk import *
from my_ide.my_ide_keil4 import *
from my_ide.my_ide_iar import *
from my_ide.my_ide_front import my_ide_front

def ide_tool_front(project_path,app_path,vendor_name,output_path,firmware_name,firmware_version):
    # 编译基线的时候，不自动运行 my_kconfig，因为基线的 tuya_iot.config 已经从云端生成了
    if os.path.basename(os.path.dirname(app_path)) == 'apps': 
        my_kconfig('./',app_path,firmware_name,firmware_version,vendor_name,1) 
    my_ide_front(project_path,app_path,vendor_name,output_path,firmware_name,firmware_version)

def ide_tool_back(OP,JSON_FILE,KIND='gcc'):    
    if KIND == 'gcc':
        ide = my_ide_gcc(JSON_FILE)
    elif KIND == 'keil':
        ide = my_ide_keil(JSON_FILE)
    elif KIND == 'cdk':
        ide = my_ide_cdk(JSON_FILE)
    elif KIND == 'keil4':
        ide = my_ide_keil4(JSON_FILE)
    elif KIND == 'iar':
        ide = my_ide_iar(JSON_FILE)
    ide.tmake()
        
    if OP == 'build':    
        ide.tbuild()
    elif OP == 'sdk':
        ide.tsdk()
    elif OP == 'flash_user':
       ide.tflash('flash_user') 
    elif OP == 'flash_all':
       ide.tflash('flash_all')        

def ide_tool_check(project_path):
    template = my_template(project_path)
    template.check()

def ide_tool_help():
    print("[error] input error")

ide_tool_check('./')
if __name__ == '__main__':
    PARAMS_NUM = len(sys.argv)-1
    if PARAMS_NUM == 0:
        ide_tool_help()
    else:
        OP = sys.argv[1]
        if (OP == 'menuconfig') and (PARAMS_NUM == 6):
            my_kconfig(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6]) 
        elif (OP == 'front') and (PARAMS_NUM == 7):
            ide_tool_front(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7])
        elif (OP == 'build' or OP == 'sdk' or OP == 'flash_user' or OP == 'flash_all') and (PARAMS_NUM == 2):
            ide_tool_back(sys.argv[1],sys.argv[2])
        else:
            ide_tool_help()



