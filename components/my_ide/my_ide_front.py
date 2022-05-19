#!/usr/bin/env python
# coding=utf-8
import sys
import os
import json

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/..')
from my_file.my_file import *

def my_ide_front(project_path,app_path,vendor_name,output_path,firmware_name,firmware_version):
    print('INPUT:\n\
    -------------------------------------\n\
    project_path:     %s\n\
    app_path:         %s\n\
    vendor_name:      %s\n\
    output_path:      %s\n\
    firmware_name:    %s\n\
    firmware_version: %s\n\
    -------------------------------------\n' 
    %(project_path,app_path,vendor_name,output_path,firmware_name,firmware_version))


    # -----------------------------------------------------------------------------------------------
    PROJECT_PATH=my_file_path_formart(project_path)
    APP_PATH=PROJECT_PATH+"/"+my_file_path_formart(app_path)
    COMP_PATH=PROJECT_PATH+"/components"
    LIBS_PATH=PROJECT_PATH+"/libs"
    INCLUDE_PATH=PROJECT_PATH+"/include"
    VENDOR_PATH=PROJECT_PATH+'/vendor/'+vendor_name
    VENDOR_JSON=VENDOR_PATH+'/toolchain/templates/vendor.json'
    CONFIG_FILE=PROJECT_PATH+"/build/tuya_iot.config"
    ADAPTER_PATH=PROJECT_PATH+"/adapter"
    SDK_CONFIG_JSON=APP_PATH+"/sdkconfig.json"


    OUTPUT_PATH=my_file_path_formart(output_path)
    FIRMWARE_NAME=firmware_name
    FIRMWARE_VERSION=firmware_version


    JSON_FILE="project.json"
    json_root={
        'output':{
            'project_path':'$ABS_PROJECT_ROOT',
            'path':OUTPUT_PATH,
            'vendor':vendor_name,
            'fw':{
                'name':FIRMWARE_NAME,
                'ver':FIRMWARE_VERSION
            }
        },
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
            'security':{},
            'include':{}
        },
    }

    # -----------------------------------------------------------------------------------------------
    print('CREATE:')
    print('    -> apps/'+my_file_path_formart(app_path))
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


    print('    -> vendor/'+vendor_name+'/tkl\n        -> drivers\n        -> system\n        -> utilities\n        -> bluetooth\n        -> security\n        -> include')
    json_root['tkl']['drivers'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/drivers")
    json_root['tkl']['system'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/system")
    json_root['tkl']['utilities'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/utilities")
    json_root['tkl']['bluetooth'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/bluetooth")
    json_root['tkl']['security'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/security")
    json_root['tkl']['include'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/include")

    print('    -> output')
    sdk_config = my_file_read_json(SDK_CONFIG_JSON)
    if sdk_config == {}:
        sdk_config = {"sdk": {"libs": []}}
    json_root['output'].update(sdk_config)

    # vendor + tool 
    print('    -> vendor/'+vendor_name+'/sdk')
    print('    -> tool')
    print('\nWRITE TO FILE...')
    my_file_save_json(JSON_FILE,json_root)
    my_file_mege_json([JSON_FILE,VENDOR_JSON],JSON_FILE)

    my_file_str_replace(JSON_FILE,PROJECT_PATH,'$PROJECT_ROOT')#PROJECT_PATH
    my_file_str_replace(JSON_FILE,'$ABS_PROJECT_ROOT',PROJECT_PATH)#PROJECT_PATH
    my_file_str_replace(JSON_FILE,'\\\\','/')#PROJECT_PATH
    


