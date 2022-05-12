#!/usr/bin/env python3
# coding=utf-8
import json
import os
import sys
import xml.etree.ElementTree as ET 

from my_ide.my_ide_base import my_ide_base

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
template_dir = current_file_dir+'/../../template'
sys.path.append(current_file_dir+'/../components')
from my_file.my_file import *
from my_exe.my_exe import my_exe_simple, my_exe_get_install_path

class my_ide_keil(my_ide_base):
    ide_kind = 'keil'
    uvprojx_path = ''
    insert_group_num = 0   

    def tmake(self):
        my_ide_base.tmake(self,'..')

    def tbuild(self):        
        print('\nBUILD')
        KEIL_PATH = my_exe_get_install_path('$KEIL_PATH')   
        UV4_PATH = KEIL_PATH+'/UV4'
        
        cmd = 'UV4.exe -j0 -b ./.log/Demo.uvprojx'
        print('> [cmd]:'+cmd)
        print('> wait about 2 min ...')
        my_exe_simple(cmd,1,UV4_PATH,None)
        
        my_ide_base.tbuild(self)

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

        tree = ET.parse(self.uvprojx_path)
        root = tree.getroot()

        if KIND == '.c' or KIND == '.lib' or KIND == '.s':
            Groups = root.find("Targets").find("Target").find("Groups")
            Group = ET.Element('Group')
            GroupName = ET.SubElement(Group, 'GroupName')
            GroupName.text = GROUP_NAME
            Files = ET.SubElement(Group, 'Files')

            kind_map = {'.c' : '1', '.lib' : '4', '.s' : '2'}

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
            tree.write(self.uvprojx_path, encoding='utf-8', xml_declaration=True)

        elif KIND == '.h':
            IncludePath = root.find("Targets").find("Target").find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("IncludePath")
            if IncludePath.text == None:
                IncludePath.text = ""

            for path in set(LIST):
                IncludePath.text = path  + ";" + IncludePath.text
            
            tree.write(self.uvprojx_path, encoding='utf-8', xml_declaration=True)

        else:
            print("KIND INPUT ERROR")
