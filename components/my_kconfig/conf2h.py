#!/usr/bin/env python3
# coding=utf-8
##
# @author huatuo
import sys
import os

def __version_string_to_hex(version,kind=None):
    version_int = 0
    nums = version.split('.')[::-1]
    if kind == 'mesh':
        nums = nums[::-1] 
        idx = 0
        while idx < len(nums):
            version_int |= ord(nums[idx]) << (idx*8)
            idx += 1
        version_hex = "{:#1x}".format(version_int)
    elif kind == 'zigbee':
        if len(nums) == 3:
            version_int = (int(nums[2]) << 6) | (int(nums[1]) << 4) | int(nums[0])
            version_hex = "{:#1x}".format(version_int)
        else:
            print("version input format error! x.x.x (max:3.3.15)")
            exit(1)
    else:
        idx = 0
        while idx < len(nums):
            version_int |= int(nums[idx]) << (idx*8)
            idx += 1
        version_hex = "{:#010x}".format(version_int)
    return version_hex
    
    

def conf2h(conf, header, fw_name, fw_version, board_name):
    header_f = open(header, 'w', encoding="utf-8")
    
    # 填充头部
    header_f.write('/*************************************************************************************/\n')
    header_f.write('/* Automatically-generated file. Do not edit! */\n')
    header_f.write('/*************************************************************************************/\n')
    header_f.write('\n')
    header_f.write('#ifndef __APP_CONFIG_H__\n')
    header_f.write('#define __APP_CONFIG_H__\n')
    header_f.write('\n')
    
    # 填充 kconfig 内容
    conf_f = open(conf, 'r', encoding="utf-8")
    conf_lines = conf_f.readlines()
    for l in conf_lines:
        l = l.strip()
        ans = ""
        if l.startswith("CONFIG_"):
            ori_key = l.split('=', 1)[0]
            ori_value = l.split('=', 1)[1]

            def_head = "#define "
            def_key = ori_key.replace("CONFIG_", '', 1) + ' '
            def_value = ori_value if ori_value != 'y' else "1"

            ans = def_head + def_key + def_value
        elif l.startswith("#"):
            ans = l.replace('#', "//", 1)
        else:
            ans = l
        header_f.write(ans+'\n')

    
    # 填充固件指纹
    header_f.write('\n//\n// FW_INFO\n//\n')
    if 'mesh' in board_name:
        header_f.write('#define BUILD_FIRMNAME          "'+fw_name+'"\n')
        header_f.write('#define FW_VERSION              "'+fw_version+'"\n')
        header_f.write('#define FW_VERSION_HEX          '+__version_string_to_hex(fw_version,'mesh')+'\n')
    elif 'zigbee' in board_name:
        header_f.write('#define BUILD_FIRMNAME          "'+fw_name+'"\n')
        header_f.write('#define FW_VERSION              "'+fw_version+'"\n')
        header_f.write('#define FW_VERSION_HEX          '+__version_string_to_hex(fw_version,'zigbee')+'\n')
    else:
        header_f.write('#define FIRMWARE_NAME           "'+fw_name+'"\n')
        header_f.write('#define FIRMWARE_VERSION        "'+fw_version+'"\n')
        header_f.write('#define FIRMWARE_VERSION_HEX    '+__version_string_to_hex(fw_version)+'\n')
        header_f.write('#define HARDWARE_VERSION        "0.1.0"\n')
        header_f.write('#define HARDWARE_VERSION_HEX    0x00000100\n')

    # 填充尾部
    header_f.write('\n\n#endif\n')
    
    header_f.close()
    conf_f.close()


if __name__ == "__main__":
    conf_file=sys.argv[1]
    h_file=sys.argv[2]
    if os.path.exists(conf_file):
        conf2h(conf_file, h_file)
    else:
        print("can't find file: ", conf_file)
        exit(1)
