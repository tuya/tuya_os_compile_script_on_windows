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

    src = {'c_files':[],'h_dirs':[],'l_files':[],'s_files':[],
           'h_dir_str':'','l_files_str':'','l_dirs_str':''}
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
                    self.src['c_files'] += area[k]
                elif k == "h_dir":
                    self.src['h_dirs'] += area[k]
                elif k == "s_files":
                    self.src['s_files'] += area[k]
                elif k == "l_files":
                    self.src['l_files'] += area[k]
                #else:            
                    #print(area[k])
    
    def tmake(self):
        # get all value
        with open(self.json_file,'r') as load_f:
            load_dict = json.load(load_f)
            self.__json_deep_search(load_dict)

        project_root = load_dict['output']['project_path']
        toolchain_path = project_root + '/' + load_dict['tool']['toochain']['bin_path']
        toolchain_evn = {**os.environ, 'PATH': toolchain_path + ';' + os.environ['PATH']}
        
        prefix = load_dict['tool']['toochain']['prefix']
        self.tool['evn'] = toolchain_evn
        self.tool['cc'] = prefix+'gcc'
        self.tool['ar'] = prefix+'ar'
        self.tool['ld'] = prefix+'ld'
        self.tool['size'] = prefix+'size'
        self.tool['objcopy'] = prefix+'objcopy'
        self.tool['objdump'] = prefix+'objdump'

        self.flag['c'] = load_dict['tool']['c_flags']
        self.flag['s'] = load_dict['tool']['s_flags']
        self.flag['ld'] = load_dict['tool']['ld_flags']

        self.macro['c'] = load_dict['tool']['c_macros']

        self.output = load_dict['output']
        self.output['sdk'].update({'components':load_dict['components']})

        my_file_clear_folder(self.output['path']) 

        # h_dirs list change to string
        for h_dir in self.src['h_dirs']:
            self.src['h_dir_str'] += (' -I'+h_dir)
       
        # get l_dirs and change to string
        # l_files change to string
        l_dirs = []
        for l_file in self.src['l_files']:
            self.src['l_files_str'] += (' -l'+os.path.splitext(os.path.basename(l_file))[0][3:])

            l_dir = os.path.dirname(l_file)
            if l_dir not in l_dirs:
                l_dirs.append(l_dir)
                self.src['l_dirs_str'] += (' -L'+l_dir)

    def tsdk(self):
        print('# 1.Create Output Package...')
        output_path     = self.output['path']
        app_path        = output_path + '/apps'
        comp_path       = output_path + '/components'
        docs_path       = output_path + '/docs'
        incs_path       = output_path + '/include'
        libs_path       = output_path + '/libs'
        scripts_path    = output_path + '/scripts'
        tools_path      = output_path + '/tools'
        log_path        = output_path + '/log'
    
        project_root = self.output['project_path']
        docs_root    = project_root+'/docs'
        include_root = project_root+'/include'
        adapter_root = project_root+'/adapter'
        
        my_file_clear_folder(app_path)
        my_file_clear_folder(comp_path)
        my_file_copy_dir_to(docs_root,docs_path)
        my_file_copy_dir_to(include_root,incs_path)
        my_file_clear_folder(libs_path)
        my_file_clear_folder(scripts_path)
        my_file_clear_folder(tools_path)
        my_file_clear_folder(log_path)
        
        my_file_copy_files_to([project_root+'/CHANGELOG.md',
                               project_root+'/LICENSE',
                               project_root+'/README.md',
                               project_root+'/RELEASE.md'],output_path)

        print('# 2.Create include/base  include/vendor/adapter...')        
        adapters = my_file_find_subdir_in_path(adapter_root)
        for adapter in adapters:
            src_path = adapter_root+'/'+adapter+'/include'
            dst_path = incs_path+'/vendor/adapter/'+adapter+'/include'
            my_file_copy_dir_to(src_path,dst_path)
            print('    [cp] cp %s to %s'%(src_path,dst_path))
            
        print('# 3.Create libs...')
        libs = self.output['sdk']['libs']
        print('-> to libs:',libs)
        for k,v in self.output['sdk']['components'].items():
            if k in libs:
                print('    ->[Y]',k)
                # create lib
                cur_lib = libs_path+'/lib'+k+'.a' 
                cur_o_files = ''

                for c_file in v['c_files']:
                    o_file = log_path+'/'+os.path.splitext(os.path.basename(c_file))[0]+'.o'
                    cur_o_files += (' '+o_file)
                    cmd = "%s %s %s -c %s -o %s %s"%(self.tool['cc'],self.flag['c'],self.src['h_dir_str'],c_file,o_file,self.macro['c'])
                    my_exe_simple(cmd,1,self.tool['evn'])
                    print("        [cc] %s"%(c_file))
                
                cmd = '%s -rc %s %s'%(self.tool['ar'],cur_lib,cur_o_files)
                my_exe_simple(cmd,1,self.tool['evn'])
                print("        [ar] %s"%(cur_lib))

                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h',incs_path+'/components/'+k+'/include')
            else:
                print('    ->[N]',k)
                # copy .c to src
                my_file_copy_files_to(v['c_files'], comp_path+'/'+k+'/src')
                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h', comp_path+'/'+k+'/include')

        print('# 4.End...')
        my_file_rm_dir(log_path)


    def tbuild(self):
        output_path = self.output['path']
        log_path = output_path+'/.log'
        my_file_clear_folder(log_path)

        o_files = log_path+'/*.o'
        elf_file = log_path+'/output.elf'
        lst_file = log_path+'/output.lst'
        bin_file = log_path+'/output.bin'

        # c to .o
        for c_file in self.src['c_files']:
            o_file = log_path+'/'+os.path.splitext(os.path.basename(c_file))[0]+'.o'
            cmd = "%s %s %s -c %s -o %s %s"%(self.tool['cc'],self.flag['c'],self.src['h_dir_str'],c_file,o_file,self.macro['c'])    
            my_exe_simple(cmd,1,self.tool['evn'])
            print("[cc] %s"%(c_file))

        # .s to .o
        for s_file in self.src['s_files']:
            o_file = log_path+'/'+os.path.splitext(os.path.basename(s_file))[0]+'.o'
            cmd = "%s %s -c %s -o %s"%(self.tool['cc'],self.flag['s'],s_file,o_file)
            my_exe_simple(cmd,1,self.tool['evn'])
            print("[cc] %s"%(s_file))

        # ld
        cmd = "%s %s %s %s \"-(\" %s \"-)\" -o %s"%(self.tool['ld'],self.flag['ld'],o_files,self.src['l_dirs_str'],self.src['l_files_str'],elf_file)
        print("\n[ld] %s"%(cmd))
        my_exe_simple(cmd,1,self.tool['evn'])

        # create list
        cmd = "%s -x -D -l -S %s > %s"%(self.tool['objdump'],elf_file,lst_file)
        print("\n[o-list] %s"%(cmd))
        my_exe_simple(cmd,1,self.tool['evn'])

        # change format
        cmd = "%s -O binary %s %s"%(self.tool['objcopy'],elf_file,bin_file)
        print("\n[o-bin] %s"%(cmd))
        my_exe_simple(cmd,1,self.tool['evn'])

        # print size
        cmd = "%s -t %s"%(self.tool['size'],elf_file)
        print("\n[o-size] %s"%(cmd))
        my_exe_simple(cmd,1,self.tool['evn'])

        DEMO_NAME = self.output['fw']['name']
        DEMO_FIRMWARE_VERSION =  self.output['fw']['ver']
        if os.path.exists(bin_file):
            print('build success')
            shutil.copy(bin_file, output_path+'/'+DEMO_NAME+'_'+DEMO_FIRMWARE_VERSION+'.bin')
            shutil.copy(bin_file, output_path+'/'+DEMO_NAME+'_UG_'+DEMO_FIRMWARE_VERSION+'.bin')
            shutil.copy(bin_file, output_path+'/'+DEMO_NAME+'_UA_'+DEMO_FIRMWARE_VERSION+'.bin')
            shutil.copy(bin_file, output_path+'/'+DEMO_NAME+'_QIO_'+DEMO_FIRMWARE_VERSION+'.bin')
            shutil.copy(bin_file, output_path+'/'+DEMO_NAME+'_PROD_'+DEMO_FIRMWARE_VERSION+'.bin')
            
            my_file_rm_dir(log_path)


