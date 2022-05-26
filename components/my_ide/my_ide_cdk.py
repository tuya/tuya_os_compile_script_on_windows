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
        
        print('\nMAX Stack Usage:==========================')
        find = 0
        if os.path.exists('Lst/Demo.htm'):
            for line in open('Lst/Demo.htm','r'):
                if 'Maximum Stack Usage' in line:
                    find = 1
                if find != 0:
                    print(line.replace('&rArr;','->').replace('<h3>','').replace('</h3>','').replace('</ul>',''),end ='')
                    find = find + 1
                    if find > 3:
                        break
        print('==========================================\n')
        
        print('RES Usage:================================')
        if os.path.exists('Lst/Demo.map'):
            for line in open('Lst/Demo.map','r'):
                if 'Total	' in line:
                    print(line,end ='')
        print('==========================================\n')
        
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
                cur_lib = '../'+libs_path+'/lib'+k+'.a' 
                output_lib = './Obj/lib'+k+'.a'
                
                sdk_cdkproj_path = '../.log/SdkDemo.cdkproj'
                sdk_cdkws_path = '../.log/SdkDemo.cdkws'
                my_file_copy_file_to_file('../.log/Demo.cdkproj',sdk_cdkproj_path)
                my_file_copy_file_to_file('../.log/Demo.cdkws',sdk_cdkws_path)

                # print('    ->[LIB]:',cur_lib)
                self.__delete_group_in_cdk(sdk_cdkproj_path)
                self.__insert_file_to_cdk(sdk_cdkproj_path,'.c',v['c_files'],'sdk')
                self.__insert_file_to_cdk(sdk_cdkproj_path,'.h',v['h_dir'],'')
                self.__make_cdk_output_lib(sdk_cdkproj_path,sdk_cdkws_path,'lib'+k)
                
                cmd = 'cdk-make.exe  --workspace=\"SdkDemo.cdkws\"   --command=\"clean\"  --project=\"Demo\"  --config=\"BuildSet\" 2>NUL 1>NUL'
                #print('\n> [cmd]:'+cmd)
                my_exe_simple(cmd,1,self.cdk_path,None)
                
                cmd = 'cdk-make.exe  --workspace=\"SdkDemo.cdkws\"   --command=\"build\"  --project=\"Demo\"  --config=\"BuildSet\" 2>NUL 1>NUL'
                #print('\n> [cmd]:'+cmd)
                my_exe_simple(cmd,1,self.cdk_path,None)
                
                
                my_file_rm_file(sdk_cdkproj_path)
                my_file_rm_file(sdk_cdkws_path)
                
                
                if os.path.exists(output_lib):
                    my_file_copy_file_to_file(output_lib,cur_lib)
                    print('        ->Success')
                else:
                    print('        ->Fail')
                    exit(0)
                    
                
                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h','../'+incs_path+'/components/'+k+'/include') 
            else:
                print('    ->[N]',k)
                # copy .c to src
                my_file_copy_files_to(v['c_files'], '../'+comp_path+'/'+k+'/src')
                # copy .h to include
                my_file_copy_one_kind_files_to(v['h_dir'],'.h', '../'+comp_path+'/'+k+'/include')      
        
        os.chdir(CURR_PATH)
    
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
    # delete_between "<Dependencies" "<BuildConfigs>" "false" $myfile (不包含起始位置）
    def __delete_group_in_cdk(self,cdkproj_path):
        find = False
        contant = ''

        for line in open(cdkproj_path,'r'):
            if '<BuildConfigs>' in line:
                find = False
            if find == False:
                contant = contant + line
            if '<Dependencies' in line:
                find = True
                
        with open(cdkproj_path,'w') as fp2:
            fp2.write(contant)
            fp2.close()
                
        
    # 将 cdk 工程切换为输出 lib 库模式
    def __make_cdk_output_lib(self,cdkproj_path,cdkws_path,output_lib):
        # 雕刻 cdkproj
        # my_file_str_replace(cdkproj_path,'<Type>Executable','<Type>Static Library')
        # my_file_str_replace(cdkproj_path,'<CallGraph>yes','<CallGraph>no')
        # my_file_str_replace(cdkproj_path,'<Map>yes','<Map>no')
        tree = ET.parse(cdkproj_path)
        root = tree.getroot()
        
        Output = root.find("BuildConfigs").find("BuildConfig").find("Output")
        
        OutputOutputName = Output.find("OutputName")
        OutputType = Output.find("Type")
        OutputCallGraph = Output.find("CallGraph")
        OutputMap = Output.find("Map")
        
        OutputOutputName.text = output_lib
        OutputType.text = 'Static Library'
        OutputCallGraph.text = 'no'
        OutputMap.text = 'no'
        
        ET.indent(tree)
        tree.write(cdkproj_path, encoding='utf-8', xml_declaration=True)
        
        # 雕刻 cdkws
        my_file_str_replace(cdkws_path,'Demo','SdkDemo')
        #my_file_str_replace(cdkws_path,'<Project Name=\"Demo\"','<Project Name=\"SdkDemo\"')
        
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
            
            ET.indent(tree)
            tree.write(cdkproj_path, encoding='utf-8', xml_declaration=True)

        elif KIND == '.h':
            IncludePath = root.find("BuildConfigs").find("BuildConfig").find("Compiler").find("IncludePath")
            if IncludePath.text == None:
                IncludePath.text = ""

            for path in set(LIST):
                IncludePath.text = path  + ";" + IncludePath.text
            
            ET.indent(tree) # format
            tree.write(cdkproj_path, encoding='utf-8', xml_declaration=True)

        else:
            print("KIND INPUT ERROR")
        
    
