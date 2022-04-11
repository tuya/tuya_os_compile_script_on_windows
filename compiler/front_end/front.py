#!/usr/bin/env python3
# coding=utf-8
import sys
import os
import json


current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/../../components')
from my_file.my_file import *

# -----------------------------------------------------------------------------------------------
# python front.py [project_path] [app_path] [vendor_name] [output_path] [firmware_name] [firmware_version]
# judge input
if len(sys.argv) != 7:
    print("[error] input error -> python front.py [project_path] [app_name] [vendor_name] [output_path] [firmware_name] [firmware_version]")
else:
    print('INPUT:\n\
    -------------------------------------\n\
    project_path:     %s\n\
    app_path:         %s\n\
    vendor_name:      %s\n\
    output_path:      %s\n\
    firmware_name:    %s\n\
    firmware_version: %s\n\
    -------------------------------------\n' 
    %(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6]))


# -----------------------------------------------------------------------------------------------
PROJECT_PATH=sys.argv[1]
APP_PATH=PROJECT_PATH+"/"+sys.argv[2]
COMP_PATH=PROJECT_PATH+"/components"
LIBS_PATH=PROJECT_PATH+"/libs"
INCLUDE_PATH=PROJECT_PATH+"/include"
VENDOR_PATH=PROJECT_PATH+'/vendor/'+sys.argv[3]
VENDOR_JSON=VENDOR_PATH+'/toolchain/templates/vendor.json'
CONFIG_FILE=PROJECT_PATH+"/build/tuya_iot.config"
ADAPTER_PATH=PROJECT_PATH+"/adapter"


OUTPUT_PATH=sys.argv[4]
FIRMWARE_NAME=sys.argv[5]
FIRMWARE_VERSION=sys.argv[6]

JSON_FILE="project.json"
json_root={
    'app':{},
    'components':{},
    'libs':{},
    'include':{},
    'adapter':{},
    'tkl':{
        'drivers':{},
        'system':{},
        'utilities':{},
        'bluetooth':{},
        'include':{}
    },
}

# -----------------------------------------------------------------------------------------------
print('CREATE:')
print('    -> apps/'+sys.argv[2])
json_root['app'] = my_file_create_subgroup(APP_PATH)


print('    -> components')
components_list=[]
for root, dirs, files in os.walk(COMP_PATH):
    components_list = dirs
    break

for component in components_list:
    print('        -> '+component)
    json_root['components'][component] = my_file_create_subgroup(COMP_PATH+"/"+component,CONFIG_FILE)


print('    -> libs')
json_root['libs'] = my_file_create_subgroup(LIBS_PATH)

print('    -> include')
json_root['include'] = my_file_create_subgroup(INCLUDE_PATH)

print('    -> adapter')
json_root['adapter'] = my_file_create_subgroup(ADAPTER_PATH,filter=".h")


print('    -> vendor/'+sys.argv[3]+'/tkl\n        -> drivers\n        -> system\n        -> utilities\n        -> bluetooth\n        -> include')
json_root['tkl']['drivers'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/drivers")
json_root['tkl']['system'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/system")
json_root['tkl']['utilities'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/utilities")
json_root['tkl']['bluetooth'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/bluetooth")
json_root['tkl']['include'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/include")


# vendor + tool + output
print('    -> vendor/'+sys.argv[3]+'/sdk')
print('    -> tool')
print('    -> output')
print('\nWRITE TO FILE...')
my_file_save_json(JSON_FILE,json_root)
my_file_mege_json([VENDOR_JSON,JSON_FILE],JSON_FILE)
my_file_str_replace(JSON_FILE,'$PROJECT_ROOT',PROJECT_PATH)

