#!/usr/bin/env python
# coding=utf-8
import sys
import os
import json

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
if current_file_dir == '':
    current_file_dir = '.'
sys.path.append(current_file_dir+'/components')
from my_ide.my_ide_gcc import *
from my_ide.my_ide_front import my_ide_front

def ide_tool_front(project_path,app_path,vendor_name,output_path,firmware_name,firmware_version):
    my_ide_front(project_path,app_path,vendor_name,output_path,firmware_name,firmware_version)

def ide_tool_back(OP,JSON_FILE):    
    ide = my_ide_gcc(JSON_FILE)
    ide.tmake()
        
    if OP == 'build':    
        ide.tbuild()
    elif OP == 'sdk':
        ide.tsdk()

def ide_tool_help():
    print("[error] input error")


if __name__ == '__main__':
    PARAMS_NUM = len(sys.argv)-1
    if PARAMS_NUM == 0:
        ide_tool_help()
    else:
        OP = sys.argv[1]
        if (OP == 'front') and (PARAMS_NUM == 7):
            ide_tool_front(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7])
        elif (OP == 'build' or OP == 'sdk') and (PARAMS_NUM == 2):
            ide_tool_back(sys.argv[1],sys.argv[2])
        else:
            ide_tool_help()



