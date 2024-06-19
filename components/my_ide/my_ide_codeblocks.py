#!/usr/bin/env python3
# coding=utf-8
import json
import os
import sys
import threading
import time

import lxml.etree as ET

from my_ide.my_ide_base import my_ide_base

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
template_dir = current_file_dir+'/../../template'
sys.path.append(current_file_dir+'/../components')
from my_file.my_file import *
from my_file.my_file_scatter import my_file_scatter
from my_exe.my_exe import my_exe_simple, my_exe_get_install_path

class my_ide_codeblocks(my_ide_base):
    ide_kind = 'codeblocks'
    cbp_path = ''
    cb_path = ''
    insert_group_num = 0   
    counter = 0

    def tmake(self):
        my_ide_base.tmake(self,'..')
        
        CODEBLOCKS_PATH = my_exe_get_install_path('$CODEBLOCKS_PATH')   
        self.cb_path = CODEBLOCKS_PATH

    def tbuild(self):        
        print('\nBUILD')
        
        self.__build_codeblocks()

    def _tlib(self,libs_path,incs_path,comp_path,log_path):
        print('# 3.Create libs...')
        evn = my_file_get_abs_path_and_formart(self.cmd['bin_path'])
        libs = self.output['sdk']['libs']
        print('-> to libs:',libs)
        
        CURR_PATH = os.getcwd()
        os.chdir('.log')
        
        for k,v in self.output['sdk']['components'].items():
            if k in libs:
                print('    ->[Y]',k)
                # create lib
                cur_lib = '../'+libs_path+'/lib'+k+'.a' 
                
                sdk_codeblocks_path = '../.log/SdkDemo.cbp'
                my_file_copy_file_to_file('../.log/Demo.cbp',sdk_codeblocks_path)

                # print('    ->[LIB]:',cur_lib)
                self.__delete_group_in_codeblocks(sdk_codeblocks_path)
                self.__insert_file_to_codeblocks(sdk_codeblocks_path,'.c',v['c_files'],'sdk')
                self.__insert_file_to_codeblocks(sdk_codeblocks_path,'.h',v['h_dir'],'')
                self.__make_codeblocks_output_lib(sdk_codeblocks_path,cur_lib)
               
                cmd = 'codeblocks.exe --rebuild --target="Release" SdkDemo.cbp --no-splash-screen'
                my_exe_simple(cmd,1,self.cb_path,None)
                
                my_file_rm_file(sdk_codeblocks_path)
                
                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h','../'+incs_path+'/components/'+k+'/include') 
            else:
                print('    ->[N]',k)
                # copy .c to src
                my_file_copy_files_to(v['c_files'], '../'+comp_path+'/'+k+'/src')
                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h', '../'+comp_path+'/'+k+'/include')
        
        # 清除掉生成 lib 时产生的中间文件
        for root, dirs, files in os.walk('../'+libs_path):
            for file in files:
                if not file.endswith('.a'):
                    my_file_rm_file(os.path.join(root,file))
            break        
        
        os.chdir(CURR_PATH)

    def _create_subgroup(self,KIND,LIST,GROUP_NAME):
        my_ide_base._create_subgroup(self,KIND,LIST,GROUP_NAME)
        if len(LIST) == 0:
            return
        
        if self.cbp_path == '':
            # copy codeblocks to output
            tmp_cbp_path      =  self.cmd['bin_path'][1:] # ../vendor -> ./vendor
            build_path        =  '.log'
            my_file_copy_dir_contents_to(tmp_cbp_path,build_path)
        
            self.cbp_path =  build_path+'/Demo.cbp' 

        self.__insert_file_to_codeblocks(self.cbp_path,KIND,LIST,GROUP_NAME)
       
       
    ###########################################################
    # codeblocks 操作内部函数
    ###########################################################
    # 将 codeblocks 工程中的 Groups 下增加的 .c、.lib 全部删除
    def __delete_group_in_codeblocks(self,cbp_path):
        tree = ET.parse(cbp_path)
        root = tree.getroot()

        Project = root.find("Project")

        Units = Project.findall("Unit")
        for Unit in Units:
            Unit.clear()

        ET.indent(tree) # format
        tree.write(cbp_path, encoding='utf-8', xml_declaration=True)

    # 将 codeblocks 工程切换为输出 lib 库模式
    def __make_codeblocks_output_lib(self,cbp_path,output_lib):
        tree = ET.parse(cbp_path)
        root = tree.getroot()

        Target = root.find("Project").find("Build").find("Target")
        Options = Target.findall("Option")

        for option in Options:
            if option.get("output") != None:
                option.set("output",output_lib)
            elif option.get("working_dir") != None:
                option.set("working_dir","")
            elif option.get("type") != None:
                option.set("type","2")

        ET.indent(tree) # format
        tree.write(cbp_path, encoding='utf-8', xml_declaration=True)

    # 将相应文件插入到 codeblocks 工程
    def __insert_file_to_codeblocks(self,cbp_path,KIND,LIST,GROUP_NAME):
        tree = ET.parse(cbp_path)
        root = tree.getroot()
        
        print(KIND,LIST)
        if KIND == '.c':
            Project = root.find("Project")

            for file in LIST:
                if file.endswith(KIND):
                    Unit = ET.Element('Unit',filename=file)
                    Files = ET.SubElement(Unit, 'Option', compilerVar="CC")
                    Project.insert(-1,Unit)

            ET.indent(tree) # format
            tree.write(cbp_path, encoding='utf-8', xml_declaration=True)
        
        elif KIND == '.h':
            Compiler = root.find("Project").find("Build").find("Target").find("Compiler")
            if Compiler == None:
                Compiler = root.find("Project").find("Compiler")

            for file in LIST:
                Add = ET.Element('Add', directory = file)
                Compiler.insert(-1,Add)

            ET.indent(tree) # format
            tree.write(cbp_path, encoding='utf-8', xml_declaration=True)
        
        elif KIND == '.lib':
            KIND = '.a'
            
            Linker =  root.find("Project").find("Build").find("Target").find("Linker")
            if Linker == None:
                Linker = root.find("Project").find("Linker")
                for file in LIST:
                    Add = ET.Element('Add', directory = file)
                    Linker.insert(-1,Add)
            else:
                Adds = Linker.findall("Add")

                for add in Adds:
                    if add.get('option') == '--start-group':
                        for file_dir in LIST:
                            if file_dir.endswith(KIND):
                                Add = ET.Element('Add', option = file_dir) 
                                add.addnext(Add)
                        break
            
            ET.indent(tree) # format
            tree.write(cbp_path, encoding='utf-8', xml_declaration=True)

    # CODEBLOCKS BUILD
    def __build_codeblocks(self):
        cmd = 'codeblocks.exe --rebuild --target="Release" ./.log/Demo.cbp --no-splash-screen'
        print('> [cmd]:'+cmd)
        print('> wait about 2 min ...')

        ret = my_exe_simple(cmd,1,self.cb_path,None)

        ret = my_ide_base.tbuild(self)
        return ret

        return 1
            
        
    
