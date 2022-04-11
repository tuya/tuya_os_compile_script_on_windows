#!/usr/bin/env python3
# coding=utf-8
import json
import os
import sys

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/../components')
from my_file.my_file import *
from my_exe.my_exe import *

class my_ide_gcc:
    json_file = ""

    c_files = []
    h_dirs = []
    l_files = []
    s_files = []

    tool = {}
    flag = {}
    macro = {}
    output = {}

    def __init__(self,JSON_FILE):
        self.json_file = JSON_FILE

    def __json_deep_search(self, area, i=0):
        for k in area:
            #print('----' * i, k, sep='')
            if  isinstance(area[k],dict):
                self.__json_deep_search(area[k], i+1)
            else:
                if k == "c_files":
                    self.c_files += area[k]
                elif k == "h_dir":
                    self.h_dirs += area[k]
                elif k == "s_files":
                    self.s_files += area[k]
                elif k == "l_files":
                    self.l_files += area[k]
                #else:            
                    #print(area[k])
    
    def tmake(self):
        # get all value
        with open(self.json_file,'r') as load_f:
            load_dict = json.load(load_f)
            self.__json_deep_search(load_dict)

        toolchain = load_dict['tool']['toochain']
        self.tool['cc'] = toolchain+'gcc'
        self.tool['ar'] = toolchain+'ar'
        self.tool['ld'] = toolchain+'ld'
        self.tool['size'] = toolchain+'size'
        self.tool['objcopy'] = toolchain+'objcopy'
        self.tool['objdump'] = toolchain+'objdump'

        self.flag['c'] = load_dict['tool']['c_flags']
        self.flag['s'] = load_dict['tool']['s_flags']
        self.flag['ld'] = load_dict['tool']['ld_flags']

        self.macro['c'] = load_dict['tool']['c_macros']

        self.output['path'] = load_dict['output']['path']

    def tbuild(self):
        my_file_clear_folder(self.output['path']) 

        # h_dirs list change to string
        h_dir_str = ''
        for h_dir in self.h_dirs:
            h_dir_str = h_dir_str + (' -I'+h_dir)
       
        # get l_dirs and change to string
        # l_files change to string
        l_files_str = ''
        l_dirs_str = ''
        l_dirs = []
        for l_file in self.l_files:
            l_files_str = l_files_str + (' -l'+os.path.splitext(os.path.basename(l_file))[0][3:])

            l_dir = os.path.dirname(l_file)
            if l_dir not in l_dirs:
                l_dirs.append(l_dir)
                l_dirs_str = l_dirs_str + (' -L'+l_dir)
        
        # c to .o
        for c_file in self.c_files:
            cmd = "%s %s %s -c %s -o %s/%s.o %s"%(self.tool['cc'],self.flag['c'],h_dir_str,c_file,self.output['path'],os.path.splitext(os.path.basename(c_file))[0],self.macro['c'])    
            #print(cmd)
            my_exe_simple(cmd,1)
            print("[cc] %s"%(c_file))

        # .s to .o
        for s_file in self.s_files:
            cmd = "%s %s -c %s -o %s/%s.o"%(self.tool['cc'],self.flag['s'],s_file,self.output['path'],os.path.splitext(os.path.basename(s_file))[0])
            #print(cmd)
            my_exe_simple(cmd,1)
            print("[cc] %s"%(s_file))

        # ld
        cmd = "%s %s %s/*.o %s \"-(\" %s \"-)\" -o %s/output.elf"%(self.tool['ld'],self.flag['ld'],self.output['path'],l_dirs_str,l_files_str,self.output['path'])
        #print(cmd)
        print("\n[ld] %s"%(cmd))
        my_exe_simple(cmd,1)

        # create list
        cmd = "%s -x -D -l -S %s/output.elf > %s/output.lst"%(self.tool['objdump'],self.output['path'],self.output['path'])
        print("\n[o-list] %s"%(cmd))
        my_exe_simple(cmd,1)

        # change format
        cmd = "%s -O binary %s/output.elf %s/output.bin"%(self.tool['objcopy'],self.output['path'],self.output['path'])
        print("\n[o-bin] %s"%(cmd))
        my_exe_simple(cmd,1)

        # print size
        cmd = "%s -t %s/output.elf"%(self.tool['size'],self.output['path'])
        print("\n[o-size] %s"%(cmd))
        my_exe_simple(cmd,1)



