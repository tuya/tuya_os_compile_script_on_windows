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

class my_ide_cdk(my_ide_base):
    ide_kind = 'cdk'
    cdkproj_path = ''
    cdk_path = ''
    insert_group_num = 0   
    counter = 0
    search_map = []

    def tmake(self):
        my_ide_base.tmake(self,'..')
        
        CDK_PATH = my_exe_get_install_path('$CDK_PATH')   
        self.cdk_path = CDK_PATH

    def tbuild(self):        
        print('\nBUILD')
        
        CURR_PATH = os.getcwd()
        os.chdir('.log')
        
        cmd = 'cdk-make.exe  --workspace=\"Demo.cdkws\"   --command=\"clean\"  --project=\"Demo\"  --config=\"BuildSet\"'
        print('\n> [cmd]:'+cmd)
        my_exe_simple(cmd,1,self.cdk_path,None)
        
        cmd = 'cdk-make.exe  --workspace=\"Demo.cdkws\"   --command=\"build\"  --project=\"Demo\"  --config=\"BuildSet\"'
        print('\n> [cmd]:'+cmd)
        my_exe_simple(cmd,1,self.cdk_path,None)
        
        cmd = self.cdk_path + '/CSKY/MinGW/csky-abiv2-elf-toolchain/bin/csky-elfabiv2-objcopy.exe -O binary ./Obj/Demo.elf ./Obj/Demo.bin'
        print('\n> [cmd]:'+cmd)
        my_exe_simple(cmd,1,self.cdk_path,None)
        
        os.chdir(CURR_PATH)
        
        my_ide_base.tbuild(self)

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
                cur_lib = '../'+libs_path+'/lib'+k+'.lib' 
                
                sdk_cdkproj_path = '../.log/SdkDemo.uvprojx'
                my_file_copy_file_to_file('../.log/Demo.uvprojx',sdk_cdkproj_path)

                # print('    ->[LIB]:',cur_lib)
                self.__delete_group_in_cdk(sdk_cdkproj_path)
                self.__insert_file_to_cdk(sdk_cdkproj_path,'.c',v['c_files'],'sdk')
                self.__insert_file_to_cdk(sdk_cdkproj_path,'.h',v['h_dir'],'')
                self.__make_cdk_output_lib(sdk_cdkproj_path,cur_lib)
                
                cmd = 'UV4.exe -j0 -b SdkDemo.uvprojx'
                my_exe_simple(cmd,1,self.cdk_path,None)
                
                my_file_rm_file(sdk_cdkproj_path)
                
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
                if not file.endswith('.lib'):
                    my_file_rm_file(os.path.join(root,file))
            break        
        
        os.chdir(CURR_PATH)
        
    def __create_lib(self,sdk_uvprojx,C_FILE_LIST,H_DIR_LIST):
        tree = ET.parse(sdk_uvprojx)
        root = tree.getroot()
    
    def _create_subgroup(self,KIND,LIST,GROUP_NAME):
        my_ide_base._create_subgroup(self,KIND,LIST,GROUP_NAME)
        if len(LIST) == 0:
            return
        
        if self.cdkproj_path == '':
            # copy cdk to output
            cdk_path         =  self.cmd['bin_path'][1:] # ../vendor -> ./vendor
            build_path        =  '.log'
            my_file_copy_dir_contents_to(cdk_path,build_path)
        
            self.cdkproj_path = build_path+'/Demo.cdkproj' 

        self.__insert_file_to_cdk(self.cdkproj_path,KIND,LIST,GROUP_NAME)
       
       
    ###########################################################
    # CDK 操作内部函数
    ###########################################################
    # 将 cdk 工程中的 Groups 下增加的 .c、.lib 全部删除
    def __delete_group_in_cdk(self,cdkproj_path):
        tree = ET.parse(cdkproj_path)
        root = tree.getroot()
        
        Groups = root.find("Targets").find("Target").find("Groups")
        Groups.clear()
            
        tree.write(cdkproj_path, encoding='utf-8', xml_declaration=True)
        
    # 将 cdk 工程切换为输出 lib 库模式
    def __make_cdk_output_lib(self,cdkproj_path,output_lib):
        tree = ET.parse(cdkproj_path)
        root = tree.getroot()
        
        TargetCommonOption = root.find("Targets").find("Target").find("TargetOption").find("TargetCommonOption")
        
        AfterMake = TargetCommonOption.find("AfterMake")
        RunUserProg1 = AfterMake.find("RunUserProg1")
        RunUserProg2 = AfterMake.find("RunUserProg2")

        RunUserProg1.text = '0'
        RunUserProg2.text = '0'
        
        CreateExecutable = TargetCommonOption.find("CreateExecutable")
        CreateLib = TargetCommonOption.find("CreateLib")
        OutputDirectory = TargetCommonOption.find("OutputDirectory")
        OutputName = TargetCommonOption.find("OutputName")
        
        CreateExecutable.text = '0'
        CreateLib.text = '1'   
        OutputDirectory.text = os.path.dirname(output_lib).replace('/','\\')+'\\'
        OutputName.text = os.path.basename(output_lib)
        
        tree.write(cdkproj_path, encoding='utf-8', xml_declaration=True)
    
    # 将相应文件插入到 cdk 工程
    def __insert_file_to_cdk(self,cdkproj_path,KIND,LIST,GROUP_NAME):
        tree = ET.parse(cdkproj_path)
        root = tree.getroot()

        if KIND == '.c' or KIND == '.lib' or KIND == '.s':
            if KIND == '.lib':
                KIND = '.a'
            if KIND == '.s':
                KIND = '.S'
            
            # 寻找是否存在 comp 或者 vendor/sdk 或者 tkl 开头的，将其合并
            father_node = None
            Groups = GROUP_NAME.split('/') 
            print('x->',Groups)
            if Groups[0] == 'comp' or (Groups[0] == 'vendor' and Groups[1] == 'sdk') or Groups[0] == 'tkl':
                # https://lxml.de/tutorial.html ElementPath
                VDs = root.findall("VirtualDirectory")
                for vd in VDs:
                    if vd.get('Name') == Groups[0]:
                        if Groups[0] == 'vendor':
                            sdk_node = vd.find('VirtualDirectory')
                            Groups = Groups[2:]
                            father_node = sdk_node
                        else:
                            Groups = Groups[1:]
                            father_node = vd
                           
                        print('-->',Groups)
                        break 
                            
            # 新增的节点树，长在 VirtualDirectoryRoot 上
            VirtualDirectoryRoot = None
            for group in reversed(Groups):
                VirtualDirectory = ET.Element('VirtualDirectory')
                VirtualDirectory.set('Name',group)
           
                if VirtualDirectoryRoot == None:
                    for file in LIST:
                        if file.endswith(KIND):
                            File = ET.SubElement(VirtualDirectory, 'File')
                            File.set("Name", file)

                            VirtualDirectory.append(File) # 添加到子级
                else:
                    VirtualDirectory.append(VirtualDirectoryRoot)
            
                VirtualDirectoryRoot = VirtualDirectory
                
            # 判断是否存在父节点，如果有，则插入到父节点上；否则插入到 Dependencies 同级
            if father_node != None:
                father_node.append(VirtualDirectoryRoot)
            else:
                Dependencies = root.find("Dependencies")
                Dependencies.addnext(VirtualDirectoryRoot)  # 添加到同级，而不是父子关系
            
            tree.write(cdkproj_path, encoding='utf-8', xml_declaration=True)

        elif KIND == '.h':
            IncludePath = root.find("BuildConfigs").find("BuildConfig").find("Compiler").find("IncludePath")
            if IncludePath.text == None:
                IncludePath.text = ""

            for path in set(LIST):
                IncludePath.text = path  + ";" + IncludePath.text
            
            tree.write(cdkproj_path, encoding='utf-8', xml_declaration=True)

        else:
            print("KIND INPUT ERROR")
        
    
