#!/usr/bin/env python3
# coding=utf-8
import os 
import sys
import subprocess
import xml.etree.ElementTree as ET
 
sys.path.append('..')
from my_exe.my_exe import my_exe_get_install_path

# 用于形成，根据编译调节 scatter 文件的类
class my_file_scatter:
    
    LOG_FILE = ''
    SCT_FILE = ''
    __GLOBAL_MODE_CNT = 999999

    # 检查 XIP 报错
    def __check_xip_flash_error(self):
        with open(self.LOG_FILE, errors='ignore') as temp_log:
            datafile = temp_log.readlines()
        for line in datafile:
            if 'ER_ROM_XIP' in line:
                return 1
            if 'ER_ROM_XIP_RE' in line:
                return 2
        return 0

    # 在 scatter 文件中查找关键词所在行
    def __find_str_line_num(self, sct_str):
        with open(self.SCT_FILE) as temp_sct:
            datafile = temp_sct.readlines()
        for num,line in enumerate(datafile):
            if sct_str in line:
                return num + 1
        return -1

    # scatter 内容块的迁移
    def __copy_line_to_new_file(self, src_file, start_line, stop_line, new_line_str):
        with open(src_file) as src_file_temp:
            datafile = src_file_temp.readlines()

        select_data = datafile[start_line : stop_line]

        sct_data = datafile[ : start_line] + datafile[ stop_line : ]
        with open(src_file, "w") as src_file_temp_d:
            src_file_temp_d.writelines(sct_data)

        with open(src_file) as src_file_temp_n:
            src_file_data_new = src_file_temp_n.readlines()

        new_line = self.__find_str_line_num(new_line_str)
        new_sct_data = src_file_data_new[ : new_line] + select_data + src_file_data_new[new_line : ]
        with open(src_file, "w") as src_file_temp_f:
            src_file_temp_f.writelines(new_sct_data)

    # xip 迁移到 xipre
    def __xip_to_xipre(self):
        start = self.__find_str_line_num("SCATTER_XIP_FILE")
        stop = self.__find_str_line_num("SCATTER_XIP_END_FILE")
        new_line = self.__find_str_line_num("SCATTER_XIP_RE_FILE")

        if(-1 == start or -1 == stop or -1 == new_line):
            return -1

        line_select_start = start
        line_select_stop = int((line_select_start + stop) / 2)
        line_select_cnt = line_select_stop - line_select_start

        if(line_select_cnt > self.__GLOBAL_MODE_CNT):
            line_select_cnt = int(self.__GLOBAL_MODE_CNT / 2)
            line_select_stop = line_select_start + line_select_cnt
        self.__GLOBAL_MODE_CNT = line_select_cnt

        self.__copy_line_to_new_file(self.SCT_FILE, line_select_start, line_select_stop, "SCATTER_XIP_RE_FILE")

        return 0

    # xipre 迁移到 xip
    def __xipre_to_xip(self):
        start = self.__find_str_line_num("SCATTER_XIP_RE_FILE")
        stop = self.__find_str_line_num("SCATTER_XIP_RE_END_FILE")
        new_line = self.__find_str_line_num("SCATTER_XIP_RE_FILE")

        if(-1 == start or -1 == stop or -1 == new_line):
            return -1

        line_select_start = start
        line_select_stop = int((line_select_start + stop) / 2)
        line_select_cnt = line_select_stop - line_select_start

        if(line_select_cnt > self.__GLOBAL_MODE_CNT):
            line_select_cnt = int(self.__GLOBAL_MODE_CNT / 2)
            line_select_stop = line_select_start + line_select_cnt
        self.__GLOBAL_MODE_CNT = line_select_cnt

        self.__copy_line_to_new_file(self.SCT_FILE, line_select_start, line_select_stop, "SCATTER_XIP_FILE")

        return 0

    def __init__(self, uvprojx_file, scatter_file, log_file):
        self.LOG_FILE = log_file
        self.SCT_FILE = scatter_file
        
        # 将 TKL\APP\COMP\LIBS 加入 scatter 文件
        insert = []
        tree = ET.parse(uvprojx_file)
        root = tree.getroot()
        Groups = root.find("Targets").find("Target").find("Groups")
        KEIL_PATH = my_exe_get_install_path('$KEIL_PATH') 
        
        for Group in Groups:
            GroupName = Group.find("GroupName")
            Files = Group.find("Files")
            if Files != None:
                for File in Files:
                    FileName = File.find("FileName")
                    FilePath = File.find("FilePath")
                    
                    if GroupName.text == None:
                        pass
                    elif GroupName.text == 'app' or \
                        GroupName.text.startswith('app/component') == True or \
                        GroupName.text.startswith('app/driver') == True or \
                        GroupName.text.startswith('tuyaos/tal') == True or \
                        GroupName.text.startswith('tuyaos/tkl') == True:
                        insert.append('        ' + os.path.splitext(FileName.text)[0] + '.o (+RO)\n')
                    elif GroupName.text.startswith('tuyaos/lib') == True or \
                        GroupName.text.startswith('app/lib') == True:
                        # insert.append('	' + os.path.splitext(FileName.text)[0] + '.lib (+RO)\n')
                        uvprojx_path = os.path.dirname(uvprojx_file)
                        lib_path = uvprojx_path + '/' + FilePath.text
                          
                        cmd = '"' + KEIL_PATH + '/ARM/ARMCC/bin/armar.exe" -t ' + lib_path 
                        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                        r = p.stdout.read().decode()
                        
                        for o_file in r.split('\r\n'):
                            #print(o_file)
                            if o_file != '':
                                insert.append('	' + o_file + ' (+RO)\n')
        
        start = self.__find_str_line_num("SCATTER_XIP_FILE")
        with open(self.SCT_FILE,'r') as sct:
            content = sct.readlines()
            content = content[:start]+insert+content[start:]
            with open(self.SCT_FILE,'wt') as sct_w:
                sct_w.writelines(content)
        
        
    def build_with_scatter_adjust(self, keil_build_func):
        for num in range(0, 5): 
            if keil_build_func() == 1:
                break
            else:
                print("\n\n--------------------------------------")
                print("Target not created, try -> %d" %(num+1))

                if (1 == self.__check_xip_flash_error()):
                    if(0 == self.__xip_to_xipre()):
                        file_log = open(self.LOG_FILE, "rb")
                        for line in file_log:
                            print(line)
                        print("Link error -- change SCT and relink ")
                        print('ER_ROM_XIP')
                    else:
                        print('build fail')
                        break
                elif (2 == self.__check_xip_flash_error()):
                    if(0 == self.__xipre_to_xip()):
                        file_log = open(self.LOG_FILE, "rb")
                        for line in file_log:
                            print(line)
                        print("Link error -- change SCT and relink ")
                        print('ER_ROM_XIP_RE')
                    else:
                        print('build fail')
                        break
                else:
                    print('build fail')
                    break
                


