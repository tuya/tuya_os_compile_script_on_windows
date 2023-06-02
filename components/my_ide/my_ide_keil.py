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

class my_ide_keil(my_ide_base):
    ide_kind = 'keil'
    uvprojx_path = ''
    uv4_path = ''
    insert_group_num = 0   
    counter = 0

    def tmake(self):
        my_ide_base.tmake(self,'..')
        
        KEIL_PATH = my_exe_get_install_path('$KEIL_PATH')   
        self.uv4_path = KEIL_PATH+'/UV4'

    def tbuild(self):        
        print('\nBUILD')
        
        # 是否需要动态调节 scatter file
        if self.cmd.__contains__('scatter_file') and self.cmd['scatter_file']['auto_adjust'] == '1':
            sct = my_file_scatter('.log/Demo.uvprojx', '.log/'+self.cmd['scatter_file']['path'], '.log/'+self.cmd['log_file'])
            sct.build_with_scatter_adjust(self.__build_keil)
        else:
            self.__build_keil()

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
                
                sdk_uvprojx_path = '../.log/SdkDemo.uvprojx'
                my_file_copy_file_to_file('../.log/Demo.uvprojx',sdk_uvprojx_path)

                # print('    ->[LIB]:',cur_lib)
                self.__delete_group_in_keil(sdk_uvprojx_path)
                self.__insert_file_to_keil(sdk_uvprojx_path,'.c',v['c_files'],'sdk')
                self.__insert_file_to_keil(sdk_uvprojx_path,'.h',v['h_dir'],'')
                self.__make_keil_output_lib(sdk_uvprojx_path,cur_lib)
                
                cmd = 'UV4.exe -j0 -b SdkDemo.uvprojx'
                my_exe_simple(cmd,1,self.uv4_path,None)
                
                my_file_rm_file(sdk_uvprojx_path)
                
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
    
    def _create_subgroup(self,KIND,LIST,GROUP_NAME):
        my_ide_base._create_subgroup(self,KIND,LIST,GROUP_NAME)
        if len(LIST) == 0:
            return
        
        if self.uvprojx_path == '':
            # copy keil to output
            keil_path         =  self.cmd['bin_path'][1:] # ../vendor -> ./vendor
            build_path        =  '.log'
            my_file_copy_dir_contents_to(keil_path,build_path)
        
            self.uvprojx_path =  build_path+'/Demo.uvprojx' 

        self.__insert_file_to_keil(self.uvprojx_path,KIND,LIST,GROUP_NAME)
       
       
    ###########################################################
    # KEIL 操作内部函数
    ###########################################################
    # 将 keil 工程中的 Groups 下增加的 .c、.lib 全部删除
    def __delete_group_in_keil(self,uvprojx_path):
        tree = ET.parse(uvprojx_path)
        root = tree.getroot()
        
        Groups = root.find("Targets").find("Target").find("Groups")
        Groups.clear()
        
        ET.indent(tree) # format        
        tree.write(uvprojx_path, encoding='utf-8', xml_declaration=True)
        
    # 将 keil 工程切换为输出 lib 库模式
    def __make_keil_output_lib(self,uvprojx_path,output_lib):
        tree = ET.parse(uvprojx_path)
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
        
        ET.indent(tree) # format
        tree.write(uvprojx_path, encoding='utf-8', xml_declaration=True)
    
    # 将相应文件插入到 keil 工程
    def __insert_file_to_keil(self,uvprojx_path,KIND,LIST,GROUP_NAME):
        tree = ET.parse(uvprojx_path)
        root = tree.getroot()

        # comp/tal_xxx -> comp
        # tal_xxx -> tal_xxx 
        GROUP_NAME_SPLIT = GROUP_NAME.split('/')
        if GROUP_NAME_SPLIT[0] == 'comp':
            GROUP_NAME = 'tal'
        elif GROUP_NAME_SPLIT[0] == 'vendor':
            GROUP_NAME = GROUP_NAME_SPLIT[0]+'/'+GROUP_NAME_SPLIT[2]
        else:
            GROUP_NAME = GROUP_NAME_SPLIT[0]

        if KIND == '.c' or KIND == '.lib' or KIND == '.s':
            kind_map = {'.c' : '1', '.lib' : '4', '.s' : '2'}
            Groups = root.find("Targets").find("Target").find("Groups")
           
            # 查找同名 Group，然后将这些同名的文件加入到一起
            GPs = Groups.findall("Group")
            gp_find = None
            for gp in GPs:
                if gp.find("GroupName").text == GROUP_NAME:
                    gp_find = gp
                    break

            if gp_find != None:
                Files = gp_find.find("Files")

                for file in LIST:
                    if file.endswith(KIND):
                        File = ET.SubElement(Files, 'File')
                        FileName = ET.SubElement(File, 'FileName')
                        FileName.text = os.path.basename(file) 
                        FileType = ET.SubElement(File, 'FileType')
                        FileType.text = kind_map[KIND]
                        FilePath = ET.SubElement(File, 'FilePath')
                        FilePath.text = file

                        Files.append(File)
            else:
                Group = ET.Element('Group')
                GroupName = ET.SubElement(Group, 'GroupName')
                GroupName.text = GROUP_NAME
                Files = ET.SubElement(Group, 'Files')

                for file in LIST:
                    if file.endswith(KIND):
                        File = ET.SubElement(Files, 'File')
                        FileName = ET.SubElement(File, 'FileName')
                        FileName.text = os.path.basename(file) 
                        FileType = ET.SubElement(File, 'FileType')
                        FileType.text = kind_map[KIND]
                        FilePath = ET.SubElement(File, 'FilePath')
                        FilePath.text = file
                Groups.insert(self.insert_group_num, Group)
                self.insert_group_num+=1
            
            ET.indent(tree) # format
            tree.write(uvprojx_path, encoding='utf-8', xml_declaration=True)

        elif KIND == '.h':
            IncludePath = root.find("Targets").find("Target").find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("IncludePath")
            if IncludePath.text == None:
                IncludePath.text = ""

            for path in set(LIST):
                IncludePath.text = path  + ";" + IncludePath.text
            
            ET.indent(tree) # format
            tree.write(uvprojx_path, encoding='utf-8', xml_declaration=True)

        else:
            print("KIND INPUT ERROR")
        
    # KEIL log 实时显示
    def __show_keil_log(self,log_file_path):
        while 1<2:
            time.sleep(0.5)
            if os.path.exists(log_file_path) and os.path.isfile(log_file_path):
                line_num = sum(1 for line in open(log_file_path, errors='ignore'))
                if line_num > self.counter:
                    with open(log_file_path, "r", errors='ignore') as fp:
                        lines = fp.readlines()
                        for line in lines[self.counter:]:
                            print(line,end='')
                        self.counter = line_num
                elif line_num < self.counter:
                    self.counter = 0
    
    # KEIL BUILD
    def __build_keil(self):
        cmd = 'UV4.exe -j0 -b ./.log/Demo.uvprojx  -o Demo.log'
        print('> [cmd]:'+cmd)
        print('> wait about 2 min ...')
        try:
            self.counter = 0
            t1 = threading.Thread(target = self.__show_keil_log, args = ('./.log/Demo.log',))
            t1.setDaemon(True)
            t1.start()
        except e:
            pass
        my_exe_simple(cmd,1,self.uv4_path,None)

        ret = my_ide_base.tbuild(self)
        return ret
            
        
    
