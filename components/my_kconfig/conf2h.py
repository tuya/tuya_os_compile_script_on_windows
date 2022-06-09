#!/usr/bin/env python3
# coding=utf-8
##
# @author huatuo
import sys
import os


def __version_string_to_hex(version):
    version_int = 0
    nums = version.split('.')[::-1]

    for idx in range(len(nums)):
        version_int |= ord(nums[idx]) << (idx*8)
        idx += 1
    
    return "{:#1x}".format(version_int)


def conf2h(conf, header, fw_name, fw_version):
    header_f = open(header, 'w', encoding="utf-8")
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

    
    header_f.write('\n//\n// FW_INFO\n//\n')
    header_f.write('#define BUILD_FIRMNAME "'+fw_name+'"\n')
    header_f.write('#define FW_VERSION "'+fw_version+'"\n')
    header_f.write('#define FW_VERSION_HEX '+__version_string_to_hex(fw_version)+'\n')

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
