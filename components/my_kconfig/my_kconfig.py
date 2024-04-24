#!/usr/bin/env python3
# coding=utf-8
import sys
import os

my_kconfig_dir = os.path.dirname(__file__)  # 当前文件所在的目录

sys.path.append('..')
from my_file.my_file import *
from my_exe.my_exe import my_exe_simple
from my_kconfig.menuconfig import menuconfig 
from my_kconfig.conf2h import conf2h


def my_kconfig(project_path,app_path,fw_name,fw_version,board_name,auto=0,gui=1):
    project_path = project_path.replace('\\','/')
    app_path = app_path.replace('\\','/')

    print('\nMY KCONFIG------------------------')
    print('INPUT:\n\
    -------------------------------------\n\
    project_path:     %s\n\
    app_path:         %s\n\
    auto:             %d\n\
    -------------------------------------\n' 
    %(project_path,app_path,auto))

    # -----------------------------------------------------------------------------------------------   
    PROJECT_PATH=my_file_path_formart(project_path)
    APP_PATH=PROJECT_PATH+"/"+my_file_path_formart(app_path)
    COMP_PATH=PROJECT_PATH+"/components"
    APP_COMP_PATH=APP_PATH+"/app.components"
    APPx_COMP_PATH=PROJECT_PATH+"/application_components"
    APP_DRIVERS_PATH=APP_PATH+"/app.drivers"
    APPx_DRIVERS_PATH=PROJECT_PATH+"/application_drivers"
    BUILD_PATH=PROJECT_PATH+"/build"
    CONFIG_FILE=BUILD_PATH+"/tuya_iot.config"


    if os.path.exists(APP_PATH+'/build'):#apps project the KCONFIG and CONFIG_FILE_BK have different name
        CONFIG_FILE_BK=APP_PATH+"/build/tuya_app.config"
        KCONFIG_FILE = BUILD_PATH+"/APPconfig"
    else:
        CONFIG_FILE_BK=APP_PATH+"/tuya_iot.config"
        KCONFIG_FILE=BUILD_PATH+"/IoTOSconfig"

    HEAD_FILE=APP_PATH+"/app_config.h"
    HEAD_FILE_BEFORE=APP_PATH+"/app_config_before.in"
    HEAD_FILE_AFTER=APP_PATH+"/app_config_after.in"


    # -----------------------------------------------------------------------------------------------   
    if auto == 0:
        # -----------------------------------------------------------------------------------------------
        print('    > CREATE Kconfig GUI:')
        kconfig_str='mainmenu "Tuya IoT Configuration"\n\n'

        kconfig_str+='menu "APP"\n'
        kcfg = APP_PATH+'/IoTOSconfig'
        if os.path.exists(kcfg):
            kconfig_str+=('\trsource\t.'+kcfg+'\n')
        kconfig_str+='endmenu\n\n'

        kconfig_str+='menu "COMP"\n'
        def append_kconfig(ITEM_PATH):
            KCONFIG_STR=''
            components_list=[]
            for root, dirs, files in os.walk(ITEM_PATH):
                components_list = dirs
                break

            for component in components_list:
                kcfg = ITEM_PATH+'/'+component+'/IoTOSconfig'
                if os.path.exists(kcfg):
                    KCONFIG_STR+=('\trsource\t.'+kcfg+'\n')
            
            return KCONFIG_STR
        
        kconfig_str += append_kconfig(COMP_PATH)
        kconfig_str += append_kconfig(APP_COMP_PATH)
        kconfig_str += append_kconfig(APPx_COMP_PATH)
        kconfig_str += append_kconfig(APP_DRIVERS_PATH)
        kconfig_str += append_kconfig(APPx_DRIVERS_PATH)
        
        kconfig_str+='endmenu\n\n'
        
        print(kconfig_str)

        # -----------------------------------------------------------------------------------------------
        print('    > WRITE TO IoTOSconfig:')
        if not os.path.exists(BUILD_PATH):
            os.makedirs(BUILD_PATH)
        
        with open(KCONFIG_FILE,'w') as fp:
            fp.write(kconfig_str)

        # -----------------------------------------------------------------------------------------------
        if gui == 1:
            print('    > SHOW MenuConfig:')
            # Get the path to the current python interpreter
            PYTHON_PATH = '"'+sys.executable+'"'
           

            cmd = PYTHON_PATH + ' ' + my_kconfig_dir + '/menuconfig.py ' + KCONFIG_FILE
            env = {'KCONFIG_CONFIG':CONFIG_FILE}
            print(cmd)
            my_exe_simple(cmd,1,env)

            # -----------------------------------------------------------------------------------------------
            print('    > Create HEAD_FILE = %s'%(HEAD_FILE))
            print('    > Copy %s To %s\n'%(CONFIG_FILE,CONFIG_FILE_BK))
            conf2h(CONFIG_FILE,HEAD_FILE,HEAD_FILE_BEFORE,HEAD_FILE_AFTER,fw_name,fw_version,board_name)    
            shutil.copy(CONFIG_FILE,CONFIG_FILE_BK)
    
    else:
        if os.path.exists(CONFIG_FILE_BK):
            print('    > Check %s exists'%(CONFIG_FILE_BK))
            print('    > Copy %s To %s'%(CONFIG_FILE_BK,CONFIG_FILE))
            if not os.path.exists(BUILD_PATH):
                os.makedirs(BUILD_PATH)
            
            shutil.copy(CONFIG_FILE_BK,CONFIG_FILE)

            print('    > Create HEAD_FILE = %s\n'%(HEAD_FILE))
            conf2h(CONFIG_FILE,HEAD_FILE,HEAD_FILE_BEFORE,HEAD_FILE_AFTER,fw_name,fw_version,board_name)    

        else:
            print('    > Check %s not exists'%(CONFIG_FILE_BK))
            print('    > Call my_kconfig to create ->')
            my_kconfig(project_path,app_path,fw_name,fw_version,board_name,0,gui)


