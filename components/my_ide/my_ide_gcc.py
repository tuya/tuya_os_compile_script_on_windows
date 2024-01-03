#!/usr/bin/env python3
# coding=utf-8
import os
import sys

from my_ide.my_ide_base import my_ide_base

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/../components')
from my_file.my_file import *
from my_exe.my_exe import my_exe_simple, my_exe_get_install_path

class my_ide_gcc(my_ide_base):
    ide_kind = 'gcc'
   
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

        # c to .o
        for c_file in self.src['c_files']:
            if c_file != "":
                self.__compile('.c',c_file,log_path,evn)
                print("[cc] %s"%(c_file))
            
        # .s to .o
        for s_file in self.src['s_files']:
            self.__compile('.s',s_file,log_path,evn)
            print("[cc] %s"%(s_file))
            
        self.var_map['$O_FILES'] = ' '.join(my_file_find_files_in_paths([log_path],'.o'))
        gcc_o_file=log_path+'/'+'gcc_o.txt'
        Note=open(gcc_o_file,mode='w')
        Note.write(self.var_map['$O_FILES'])
        Note.close()
        # ld
        cmd = self.cmd['ld']
        print("\n[ld] %s"%(cmd))
        my_exe_simple(cmd,1,evn,self.var_map)

        # create list
        cmd = self.cmd['objdump']
        print("\n[o-list] %s"%(cmd))
        my_exe_simple(cmd,1,evn,self.var_map)

        # change format
        cmd = self.cmd['objcopy']
        print("\n[o-bin] %s"%(cmd))
        my_exe_simple(cmd,1,evn,self.var_map)

        # print size
        cmd = self.cmd['size']
        print("\n[o-size] %s"%(cmd))
        my_exe_simple(cmd,1,evn,self.var_map)

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
                cur_o_files = ''

                for c_file in v['c_files']:
                    o_file = self.__compile('.c',c_file,log_path,evn)
                    cur_o_files += (' '+o_file)
                    print("        [cc] %s"%(c_file))
                
                cmd = '%s -rc %s %s'%(self.cmd['ar'],cur_lib,cur_o_files)
                my_exe_simple(cmd,1,evn,self.var_map)
                print("        [ar] %s"%(cur_lib))

                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h',incs_path+'/components/'+k+'/include')
            else:
                print('    ->[N]',k)
                # copy .c to src
                my_file_copy_files_to(v['c_files'], comp_path+'/'+k+'/src')
                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h', comp_path+'/'+k+'/include')


    def if_need_rebuild(self,dep_file):
        with open(dep_file,"r") as f:
            list_line1 = f.readline().split(' ')
            if(list_line1[1] != '\\\n'):
                try:
                    if(os.path.getmtime(list_line1[1]) > os.path.getmtime(dep_file)):
                        return True
                except:
                    return True
            for line in f.readlines():
                line = line.lstrip()
                line = line.strip('\n')
                line = line.replace(":", " ")
                list_n = line.split(' ')
                for file in list_n:
                    if(file == '\\'):
                        continue
                    if(file == ""):
                        continue
                    try:
                        if(os.path.getmtime(file) > os.path.getmtime(dep_file)):
                            return True
                    except:
                        print("file not exit")
                        return True
        return False


    def __compile(self,kind,file,out_path,evn):
        cc = self.cmd['gcc']['cc']
        asm = self.cmd['gcc']['asm']
        c_flags = self.cmd['gcc']['c_flags']
        c_macros = self.cmd['gcc']['c_macros']
        s_flags = self.cmd['gcc']['s_flags']
        
        o_file = out_path+'/'+os.path.splitext(os.path.basename(file))[0]+'.o'
        d_file = o_file+'.d'
        
        if kind == '.c':
            gcc_h_file = out_path+'/'+'gcc_h.txt'
            Note=open(gcc_h_file,mode='w')
            Note.write(self.src['h_dir_str'])
            Note.close()

            if((os.path.exists(o_file) == True) and (os.path.exists(d_file) == True) and (self.if_need_rebuild(d_file) == False)):
                return o_file
            if (os.path.exists(o_file)):
                my_file_rm_file(o_file)
            cmd = "%s %s @%s -c %s -o %s %s -MMD -MF %s"%(cc,c_flags,gcc_h_file,file,o_file,c_macros, d_file)
        elif kind == '.s':
            gcc_h_file = out_path+'/'+'gcc_h.txt'
            Note=open(gcc_h_file,mode='w')
            Note.write(self.src['h_dir_str'])
            Note.close()

            if((os.path.exists(o_file) == True) and (os.path.exists(d_file) == True) and (self.if_need_rebuild(d_file) == False)):
                return o_file
            if (os.path.exists(o_file)):
                my_file_rm_file(o_file)

            cmd = "%s %s @%s -c %s -o %s"%(asm,s_flags,gcc_h_file,file,o_file)
            
        my_exe_simple(cmd,1,evn,self.var_map)
        
        return o_file
    

