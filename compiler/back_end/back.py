#!/usr/bin/env python3
# coding=utf-8
import sys
import os
import json


current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/../../components')
from my_file.my_file import *
from my_exe.my_exe import *
from my_ide.my_ide_gcc import *

# -----------------------------------------------------------------------------------------------
if len(sys.argv) != 2:
    print("[error] input error -> python back.py [project_json]")
else:
    print('INPUT:\n\
    -------------------------------------\n\
    project_json:     %s\n\
    -------------------------------------\n' 
    %(sys.argv[1]))

# -----------------------------------------------------------------------------------------------
JSON_FILE=sys.argv[1]
ide = my_ide_gcc(JSON_FILE)
ide.tmake()
ide.tbuild()


