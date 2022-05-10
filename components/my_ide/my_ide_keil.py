#!/usr/bin/env python3
# coding=utf-8
import json
import os
import sys
import xml.etree.ElementTree as ET 

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
template_dir = current_file_dir+'/../../template'
sys.path.append(current_file_dir+'/../components')
from my_file.my_file import *
from my_exe.my_exe import my_exe_simple, my_exe_add_env_path

class my_ide_keil:
    uvprojx_path = ''
    insert_group_num = 0

    json_file = ""

    src = {'c_files':[],'h_dirs':[],'l_files':[],'s_files':[],
           'h_dir_str':'','l_files_str':'','l_dirs_str':''}
    tool = {}
    flash = {}
    flag = {}
    macro = {}
    output = {}

    def __init__(self,JSON_FILE):
        self.json_file = JSON_FILE

    def __json_deep_search(self, area, group_name='', i=0):
        for k in area:
            #print('----' * i, k, sep='')
            if  isinstance(area[k],dict):
                old_group_name = group_name
                if group_name == '':
                    group_name = k
                else:
                    group_name = group_name+'/'+k

                self.__json_deep_search(area[k], group_name, i+1)
                group_name = old_group_name
            else:
                if k == "c_files":
                    print(group_name)
                    self.__create_subgroup(self.uvprojx_path,'.c',area[k],group_name)
                elif k == "h_dir":
                    self.__create_subgroup(self.uvprojx_path,'.h',area[k],'')
                elif k == "s_files":
                    self.__create_subgroup(self.uvprojx_path,'.s',area[k],group_name+'/s')
                elif k == "l_files":
                    self.__create_subgroup(self.uvprojx_path,'.lib',area[k],group_name+'/libs')
                #else:            
                    #print(area[k])
    

    def __create_subgroup(self,UVPROJX_PATH,KIND,LIST,GROUP_NAME):
        if len(LIST) == 0:
            return

        tree = ET.parse(UVPROJX_PATH)
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
            tree.write(UVPROJX_PATH, encoding='utf-8', xml_declaration=True)

        elif KIND == '.h':
            IncludePath = root.find("Targets").find("Target").find("TargetOption").find("TargetArmAds").find("Cads").find("VariousControls").find("IncludePath")
            if IncludePath.text == None:
                IncludePath.text = ""

            for path in set(LIST):
                IncludePath.text = path  + ";" + IncludePath.text
            
            tree.write(UVPROJX_PATH, encoding='utf-8', xml_declaration=True)

        else:
            print("KIND INPUT ERROR")


    def tmake(self):
        # get all value
        with open(self.json_file,'r') as load_f:
            load_dict = json.load(load_f)
            
            project_root      =  load_dict['output']['project_path']
            output_path       =  (load_dict['output']['path']).replace('$PROJECT_ROOT',project_root)
            keil_path         =  (load_dict['tool']['keil']['toolchain']['bin_path']).replace('$PROJECT_ROOT',project_root)
            self.uvprojx_path =  output_path+'/keil/Demo.uvprojx' 
            # copy keil to output
            my_file_copy_dir_to(keil_path,output_path+'/keil')
            
            self.insert_group_num = 0
            self.__json_deep_search(load_dict)

            my_file_str_replace(self.uvprojx_path,'$PROJECT_ROOT','../..') 

    def tsdk(self):
        print('tsdk')

    def tbuild(self):        
        print('tbuild')    

    def tflash(self,OP):
        print('tflash')
