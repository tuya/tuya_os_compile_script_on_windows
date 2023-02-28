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
    APP_COMP_PATH=APP_PATH+"/app.components"
    APPx_COMP_PATH=PROJECT_PATH+"/application_components"
    LIBS_PATH=PROJECT_PATH+"/libs"
    APP_LIBS_PATH=APP_PATH+"/app.libs"
    INCLUDE_PATH=PROJECT_PATH+"/include"
    VENDOR_PATH=PROJECT_PATH+'/vendor/'+vendor_name
    VENDOR_JSON=VENDOR_PATH+'/toolchain/templates/vendor.json'
    CONFIG_FILE=PROJECT_PATH+"/build/tuya_iot.config"
    ADAPTER_PATH=PROJECT_PATH+"/adapter"
    SDK_CONFIG_JSON=APP_PATH+"/sdkconfig.json"
    DEPEND_JSON=APP_PATH+"/depend.json"


    OUTPUT_PATH=my_file_path_formart(output_path)
    FIRMWARE_NAME=firmware_name
    FIRMWARE_VERSION=firmware_version


    JSON_FILE="project.json"
    json_root={
        'output':{
            'project_path':'$ABS_PROJECT_ROOT',
            'path':OUTPUT_PATH,
            'kind':os.path.basename(os.path.dirname(app_path)),
            'vendor':vendor_name,
            'fw':{
                'name':FIRMWARE_NAME,
                'ver':FIRMWARE_VERSION
            }
        },
        'app':{},
        'components':{},
        'application_components':{},
        'libs':{},
        'app_libs':{},
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

    # 应用目录中的 component（一般时应用组件）
    print('    -> application_components')
    application_components_list=[]
    for root, dirs, files in os.walk(APP_COMP_PATH):
        application_components_list = dirs
        break

    for component in application_components_list:
        print('        -> '+component)
        json_root['application_components'][component] = my_file_create_subgroup(APP_COMP_PATH+"/"+component,CONFIG_FILE)

    # 根目录中的应用 component（一般时品类组件）
    print('    -> application_components')
    application_components_list=[]
    for root, dirs, files in os.walk(APPx_COMP_PATH):
        application_components_list = dirs
        break

    for component in application_components_list:
        print('        -> '+component)
        json_root['components'][component] = my_file_create_subgroup(APPx_COMP_PATH+"/"+component,CONFIG_FILE)

    print('    -> app libs')
    json_root['app_libs'] = my_file_create_subgroup(APP_LIBS_PATH)


    # 按需加载基线的开源与闭源组件<docs/03-xxx>
    depend = my_file_read_json(DEPEND_JSON)
    if depend == {}:
        # 根目录中的 components（一般是基线的开源组件，品类在 cde 上配置在老的组件列，也会放在这里，这种方式已经渐渐弃用了）
        print('    -> components')
        components_list=[]
        for root, dirs, files in os.walk(COMP_PATH):
            components_list = dirs
            break

        for component in components_list:
            print('        -> '+component)
            json_root['components'][component] = my_file_create_subgroup(COMP_PATH+"/"+component,CONFIG_FILE)

        # 基线的闭源库    
        print('    -> libs')
        json_root['libs'] = my_file_create_subgroup(LIBS_PATH)

        # 基线的头文件
        print('    -> include')
        json_root['include'] = my_file_create_subgroup(INCLUDE_PATH)
    else:
        # 按照 depend.json 指定的基线中的开源组件进行加载
        print('    -> components')
        components_list=depend['base']['components']
        for component in components_list:
            print('        -> '+component)
            json_root['components'][component] = my_file_create_subgroup(COMP_PATH+"/"+component,CONFIG_FILE)

        # 按照 depend.json 指定的基线中的闭源组建进行加载
        print('    -> libs')
        h_list=[]
        c_list=[]
        l_list=[]
        libs_list=depend['base']['libs']
        for lib in libs_list:
            print('        -> '+lib)
            lib_name = lib.split(".")[0]
            if lib_name.startswith('lib'):
                lib_name = lib_name[3:]
            
            lib_path = "$PROJECT_ROOT/libs/"+lib
            lib_head_file_path = "$PROJECT_ROOT/include/components/"+lib_name+"/include"
            l_list.append(lib_path)
            h_list.append(lib_head_file_path)
            
        json_root['libs'] = {'c_files':list(set(c_list)),'h_dir':list(set(h_list)),'l_files':list(set(l_list))}
        json_root['include']['vendor'] = my_file_create_subgroup(INCLUDE_PATH+'/vendor')
        json_root['include']['base'] = my_file_create_subgroup(INCLUDE_PATH+'/base')

# vendor 中的各种文件
    print('    -> adapter')
    json_root['adapter'] = my_file_create_subgroup(ADAPTER_PATH,filter=".h")


    print('    -> vendor/'+vendor_name+'/tkl\n        -> drivers\n        -> system\n        -> utilities\n        -> bluetooth\n        -> zigbee\n        -> security\n        -> include')
    json_root['tkl']['drivers'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/drivers")
    json_root['tkl']['system'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/system")
    json_root['tkl']['utilities'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/utilities")
    json_root['tkl']['bluetooth'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/bluetooth")
    json_root['tkl']['zigbee'] = my_file_create_subgroup(VENDOR_PATH+"/tuyaos/zigbee")
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
    


