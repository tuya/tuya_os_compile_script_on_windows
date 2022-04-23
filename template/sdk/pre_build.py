# coding:utf-8
import os
import sys
import json
import collections

#*****************************************************************#
# NOTE: This script is a compiled script. Please do not modify it #
#*****************************************************************#
# Pre Build processing.

# Parameter description：
# $1 - Application project name: tuyaos_demo_ble_peripheral
# $2 - Application project version: 1.0.0
# python prebuild.py tuyaos_demo_ble_peripheral 1.0.0

PROJECT_ROOT_PATH="..\\"
DEMO_PATH = PROJECT_ROOT_PATH+sys.argv[1]
DEMO_NAME = sys.argv[2]
DEMO_FIRMWARE_VERSION = sys.argv[3]

TABLE_SPACE = 40

DEMO_CONFIG_NAME = 'appconfig.json'
DEMO_CONFIG_PATH = os.path.join(DEMO_PATH, DEMO_CONFIG_NAME)
DEMO_SRC_PATH = os.path.join(DEMO_PATH, 'src')
DEMO_INC_PATH = os.path.join(DEMO_PATH, 'include')


def version_string_to_hex(version):
    str = version.split('.')
    version_int = ((ord(str[1]) << 8) | ord(str[0]))
    version_hex = "{:#1x}".format(version_int)
    return version_hex
    
def hw_version_string_to_hex(version):
    str = version.split('.')
    version_int = ((ord(str[0]) << 16) | (ord(str[1]) << 8) | ord(str[2]))
    version_hex = "{:#1x}".format(version_int)
    return version_hex


def app_config_firmware_info_get():
    global DEMO_HARDWARE_VERSION
    global DEMO_MESH_CATEGORY
    global DEMO_PRODUCTKEY
    global DEMO_IS_FIRMWARE_KEY
    global DEMO_NEED_PUBLISH_ADDR

    print("app_config firmware information parse start...")
    file = open(DEMO_CONFIG_PATH, 'rb')
    fileJson = json.load(file, object_pairs_hook = collections.OrderedDict)
    DEMO_HARDWARE_VERSION = fileJson['firmware_info']['hardware_version']

    DEMO_MESH_CATEGORY = fileJson['product_info']['mesh_category']
    DEMO_PRODUCTKEY = fileJson['product_info']['product_key']
    DEMO_IS_FIRMWARE_KEY = fileJson['product_info']['is_firmware_key']
    DEMO_NEED_PUBLISH_ADDR = fileJson['product_info']['need_publish_addr']
    file.close()
    print("app_config firmware information parse success")


def generate_file_header(func):
    def wrapper(*args, **kwargs):
        print("file header generate start...")
        fileObject = open(args[0], 'w')
        fileObject.writelines("/*************************************************************************************/" + '\n')
        fileObject.writelines("/* Automatically-generated file. Do not edit! */" + '\n')
        fileObject.writelines("/*************************************************************************************/" + '\n\n')
        fileObject.close()
        print("file header generate finish...")
        return func(*args,**kwargs)
    return wrapper


def __generate_app_config_c(fileObj):

    fileObj.writelines("#include \"app_config.h\"" + '\n')
    fileObj.writelines("#include \"tuya_iot_config.h\"" + '\n')
    fileObj.writelines("#include \"tuya_ble_main.h\"" + '\n\n\n\n\n')

    fileObj.writelines("OPERATE_RET app_config_info_set(VOID_T)" + '\n')
    fileObj.writelines("{" + '\n')
    
    fileObj.writelines("    tal_common_info_t tal_common_info   = {0};" + '\n')
    fileObj.writelines("    tal_common_info.p_firmware_name     = (UINT8_T*)FIRMWARE_NAME;" + '\n')
    fileObj.writelines("    tal_common_info.p_firmware_version  = (UINT8_T*)FIRMWARE_VERSION;" + '\n')
    fileObj.writelines("    tal_common_info.firmware_version    = FIRMWARE_VERSION_HEX;" + '\n')
    fileObj.writelines("    tal_common_info.p_hardware_version  = (UINT8_T*)HARDWARE_VERSION;" + '\n')
    fileObj.writelines("    tal_common_info.hardware_version    = HARDWARE_VERSION_HEX;" + '\n')
    fileObj.writelines("    tal_common_info.p_sdk_version       = (UINT8_T*)\"0.0.9\";" + '\n')
    fileObj.writelines("    tal_common_info.p_kernel_version    = (UINT8_T*)\"0.0.1\";" + '\n')
    fileObj.writelines("    return tal_common_info_init(&tal_common_info);" + '\n')

    fileObj.writelines("}" + '\n\n')


def __generate_app_config_h(fileObj):

    fileObj.writelines("#ifndef __APP_CONFIG_H__" + '\n')
    fileObj.writelines("#define __APP_CONFIG_H__" + '\n\n')
    fileObj.writelines("#include \"tuya_cloud_types.h\"" + '\n\n')
    fileObj.writelines("/* automatically generated app firmware information! */" + '\n')

    fileObj.writelines("#define BUILD_FIRMNAME".ljust(TABLE_SPACE) + '\"' + DEMO_NAME + '\"' + '\n')
    fileObj.writelines("#define FW_VERSION".ljust(TABLE_SPACE) + '\"' + DEMO_FIRMWARE_VERSION + '\"' + '\n')
    fileObj.writelines("#define FW_VERSION_HEX".ljust(TABLE_SPACE) + version_string_to_hex(DEMO_FIRMWARE_VERSION) + '\n')
    fileObj.writelines("#define HARDWARE_VERSION".ljust(TABLE_SPACE) + '\"' + DEMO_HARDWARE_VERSION + '\"' + '\n')
    fileObj.writelines("#define HARDWARE_VERSION_HEX".ljust(TABLE_SPACE) + hw_version_string_to_hex(DEMO_HARDWARE_VERSION) + '\n\n')
    
    fileObj.writelines("#define MESH_CATEGORY".ljust(TABLE_SPACE) + '0x' + DEMO_MESH_CATEGORY + '\n')
    fileObj.writelines("#define PRODUCTKEY".ljust(TABLE_SPACE) + '\"' + DEMO_PRODUCTKEY + '\"' + '\n')
    fileObj.writelines("#define IS_FIRMWARE_KEY".ljust(TABLE_SPACE) + DEMO_IS_FIRMWARE_KEY + '\n')
    fileObj.writelines("#define NEED_PUBLISH_ADDR".ljust(TABLE_SPACE) + DEMO_NEED_PUBLISH_ADDR + '\n')

    fileObj.writelines("#endif" + '\n\n')
    fileObj.close()


@generate_file_header
def generate_app_config_c(*args, **kwargs):
    fileObject = open(args[0], 'a+')

    __generate_app_config_c(fileObject)

    fileObject.close()
    print(args[0]+" generate success")


@generate_file_header
def generate_app_config_h(*args, **kwargs):

    fileObject = open(args[0], 'a+')

    __generate_app_config_h(fileObject)

    print(args[0]+" generate success")


if __name__ == "__main__":
    print("\r\n> prebuild ------------------------------------")
    app_config_firmware_info_get()
    inc_path = os.path.join(DEMO_INC_PATH, 'app_config.h')
    src_path = os.path.join(DEMO_SRC_PATH, 'app_config.c')
    generate_app_config_h(inc_path)
    #generate_app_config_c(src_path)
    print("\r\n> prebuild end------------------------------------")


