#!/usr/bin/env python
# coding=utf-8
import sys
import os
import json

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/..')
from my_file.my_file import *

def _front_components(ITEM_PATH,JSON_ROOT,KEY,CONFIG_FILE,DEPEND):
    if os.path.exists(ITEM_PATH) == False:
        return

    if DEPEND == {}:
        print('    -> '+KEY)
        item_list=[]
        for root, dirs, files in os.walk(ITEM_PATH):
            item_list = dirs
            break

        for item in item_list:
            print('        -> '+item)
            JSON_ROOT[KEY][item] = my_file_create_subgroup(ITEM_PATH+"/"+item,CONFIG_FILE)
    else:
        # 按照 depend.json 指定的基线中的开源组件进行加载
        print('    -> '+KEY)

        components_list=DEPEND['base']['components']
        for component in components_list:
            if os.path.exists(ITEM_PATH+"/"+component):
                print('        -> '+component)
                JSON_ROOT[KEY][component] = my_file_create_subgroup(ITEM_PATH+"/"+component,CONFIG_FILE)

                # Zibgee 工程生成的开源库，其 .c 和蓝牙一样放置; 其 .h 放置方式和 lib 方式一样（放在 include/components/xxx/include 中）
                # 为了兼容，做下面处理
                lib_head_file_path = "include/components/"+component+"/include"
                if os.path.exists(lib_head_file_path):
                    JSON_ROOT[KEY][component]['h_dir'] = '$PROJECT_ROOT/'+lib_head_file_path

def _front_libs(APP_LIBS_PATH,LIBS_PATH,INCLUDE_PATH,JSON_ROOT,DEPEND):

    if DEPEND == {}:
        # 品类的闭源库(品类的库及头文件放在一个目录下)
        print('    -> app libs')
        JSON_ROOT['app_libs'] = my_file_create_subgroup(APP_LIBS_PATH)

        # 基线的闭源库(基线的库和头文件放在不同目录下)
        print('    -> libs')
        JSON_ROOT['libs'] = my_file_create_subgroup(LIBS_PATH)

        # 基线的头文件
        print('    -> include')
        JSON_ROOT['include'] = my_file_create_subgroup(INCLUDE_PATH)
    else:
        # 按照 DEPEND.json 指定的基线中的闭源组建进行加载
        print('    -> libs')
        l_list=[]
        app_l_list=[]
        libs_list=DEPEND['base']['libs']
        for lib in libs_list:
            print('        -> '+lib)
            lib_name = lib.split(".")[0]
            if lib_name.startswith('lib'):
                lib_name = lib_name[3:]
            
            lib_path = LIBS_PATH+lib
            app_lib_path = APP_LIBS_PATH+lib
            if os.path.exists(lib_path):
                l_list.append(lib_path) 
            elif os.path.exists(app_lib_path):
                app_l_list.append(app_lib_path)

            lib_head_file_path = "include/components/"+lib_name+"/include"
            if os.path.exists(lib_head_file_path):
                H_LIST.append('$PROJECT_ROOT/'+lib_head_file_path)

        JSON_ROOT['app_libs'] = {'l_files':list(dict.fromkeys(app_l_list))}
        JSON_ROOT['libs'] = {'h_dir':list(dict.fromkeys(H_LIST)),'l_files':list(dict.fromkeys(l_list))}
        JSON_ROOT['include']['vendor'] = my_file_create_subgroup(INCLUDE_PATH+'/vendor')
        JSON_ROOT['include']['base'] = my_file_create_subgroup(INCLUDE_PATH+'/base')


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
    APP_DRIVERS_PATH=APP_PATH+"/app.drivers"
    APPx_DRIVERS_PATH=PROJECT_PATH+"/application_drivers"
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
        'app_libs':{},
        'application_components':{},
        'application_drivers':{},
        'libs':{},
        'components':{},
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
    json_root['app'] = my_file_create_subgroup(APP_PATH,CONFIG_FILE)

    # 按需加载基线的开源与闭源组件<docs/03-xxx>
    depend = my_file_read_json(DEPEND_JSON)
    _front_components(APP_COMP_PATH,json_root,"application_components",CONFIG_FILE,depend)    # 应用目录中的 component（一般是应用组件）
    _front_components(APPx_COMP_PATH,json_root,"application_components",CONFIG_FILE,depend)   # 应用目录中的 component（一般是品类组件）
    _front_components(APP_DRIVERS_PATH,json_root,"application_drivers",CONFIG_FILE,depend)    # 应用目录中的 drivers  （一般是应用组件）
    _front_components(APPx_DRIVERS_PATH,json_root,"application_drivers",CONFIG_FILE,depend)   # 应用目录中的 drivers  （一般是品类组件）

    # 根目录中的 components（一般是基线的开源组件，品类在 cde 上配置在老的组件列，也会放在这里，这种方式已经渐渐弃用了）
    _front_components(COMP_PATH,json_root,"components",CONFIG_FILE,depend)

    _front_libs(APP_LIBS_PATH,LIBS_PATH,INCLUDE_PATH,json_root,depend)

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
    


