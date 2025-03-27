#!/usr/bin/env python
# coding=utf-8
import os
import sys

from my_ide.my_ide_base import my_ide_base

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/../components')
from my_file.my_file import *
from my_exe.my_exe import my_exe_simple, my_exe_get_install_path

class my_ide_self(my_ide_base):
    ide_kind = 'self'
   
    def tmake(self):
        my_ide_base.tmake(self)
    
    def tbuild(self): 
        print('\nBUILD')    
        evn = my_file_get_abs_path_and_formart(self.cmd['bin_path'])
        print('> [evn path]:',evn)
        log_path = self.var_map['$OUTPUT']

        # before build
        for cmd in self.cmd['before-build']:
            my_exe_simple(cmd,1,evn,self.var_map)
            print("\n[o-before-build] %s"%(cmd))
        
        # build 
        for cmd in self.cmd['build']:
            self_src_json = log_path+'/self_src.json'
            cmd = f"{cmd} {self_src_json}"
            my_file_save_json(self_src_json,self.src)          
            my_exe_simple(cmd,1,evn,self.var_map)
            print("\n[o-build] %s"%(cmd))
        
        # after build
        for cmd in self.cmd['after-build']:
            print("\n[o-after-build] %s"%(cmd))
            my_exe_simple(cmd,1,evn,self.var_map)
        
        my_ide_base.tbuild(self)

    def _tlib(self,libs_path,incs_path,comp_path,log_path):
        print('# 3.Create libs...')
        evn = my_file_get_abs_path_and_formart(self.cmd['bin_path'])
        libs = self.output['sdk']['libs']
        print('-> to libs:',libs)
        for k,v in self.output['sdk']['components'].items():
            if k in libs:
                print('    ->[Y]',k)
                # create lib
                cur_lib = libs_path+'/lib'+k+'.a' 
                
                for cmd in self.cmd['create_lib']:
                    cmd = f"{cmd} {v['c_files']} {cur_lib}"
                    my_exe_simple(cmd,1,evn,self.var_map)
                    print("\n[o-create-lib] %s"%(cmd))

                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h',incs_path+'/components/'+k+'/include')
            else:
                print('    ->[N]',k)
                # copy .c to src
                my_file_copy_files_to(v['c_files'], comp_path+'/'+k+'/src')
                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h', comp_path+'/'+k+'/include')
