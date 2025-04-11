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

class my_ide_ccs(my_ide_base):
    ide_kind = 'ccs'
    ccsproj_path = ''
    cproj_path = ''
    proj_path = ''
    ccs_path = ''
    insert_h_dir_num = 0   
    counter = 0

    def tmake(self):
        my_ide_base.tmake(self,'..')
        
        CCS_PATH = my_exe_get_install_path('$CCS_PATH')   
        self.ccs_path = CCS_PATH

    def tbuild(self):        
        print('\nBUILD')
        
        self.__build_ccs("app_project")

    def _tlib(self,libs_path,incs_path,comp_path,log_path):
        print('# 3.Create libs...')
        libs = self.output['sdk']['libs']
        print('-> to libs:',libs)
        
        CURR_PATH = os.getcwd()
        os.chdir('.log')
       
        self.__cp_include_path_from_app_project_to_lib_project("app_project/.cproject", "lib_project/.cproject")

        for k,v in self.output['sdk']['components'].items():
            if k in libs:
                print('    ->[Y]',k)
                # create lib
                cur_lib = '../'+libs_path+'/lib'+k+'.lib' 
                
                # print('    ->[LIB]:',cur_lib)
                my_file_copy_dir_to("./lib_project","./lib_project_tmp")
                lib_ccsproj_path =  './lib_project_tmp/.ccsproject' 
                lib_cproj_path = './lib_project_tmp/.cproject' # .h 搜索空间在这里配置 
                lib_proj_path =  './lib_project_tmp/.project' # .c 通过 URI 链接进入工程 

                self.__insert_file_to_ccs(lib_ccsproj_path,lib_cproj_path,lib_proj_path,'.c',v['c_files'],k)
                self.__insert_file_to_ccs(lib_ccsproj_path,lib_cproj_path,lib_proj_path,'.h',v['h_dir'],'')

                self.__build_ccs("lib_project_tmp",is_lib=True)
                
                gen_lib_path = "./lib_project_tmp/Release/tuyaos_lib.lib"
                if os.path.exists(gen_lib_path):
                    print(cur_lib)
                    my_file_copy_file_to_file(gen_lib_path,cur_lib) 
                else:
                    print("ERROR!!!")
                    exit(0)
                
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
        
        if self.ccsproj_path == '':
            # copy ccs to output
            ccs_path         =  self.cmd['bin_path'][1:] # ../vendor -> ./vendor
            build_path        =  '.log'
            my_file_copy_dir_to(ccs_path+"/app_project",build_path+"/app_project")
            my_file_copy_dir_to(ccs_path+"/lib_project",build_path+"/lib_project")
        
            self.ccsproj_path =  build_path+'/app_project/.ccsproject' 
            self.cproj_path =  build_path+'/app_project/.cproject' # .h 搜索空间在这里配置 
            self.proj_path =  build_path+'/app_project/.project' # .c 通过 URI 链接进入工程 

        self.__insert_file_to_ccs(self.ccsproj_path,self.cproj_path,self.proj_path,KIND,LIST,GROUP_NAME)
       
       
    ###########################################################
    # CCS 操作内部函数
    ###########################################################
    # 从 app_project 中提取所有包含头文件，作用于打库工程 lib_project
    def __cp_include_path_from_app_project_to_lib_project(self,cproj_from,cproj_to):
        print(f"> cp_include_path_from_app_project_to_lib_project:\n  {cproj_from}\n  {cproj_to}")
        from_cproj_tree = ET.parse(cproj_from)
        from_cproj_root = from_cproj_tree.getroot()
        to_cproj_tree = ET.parse(cproj_to)
        to_cproj_root = to_cproj_tree.getroot()
            
        # 使用 XPath 查找所有 option 元素，其 valueType 属性为 includePath
        from_option_include_path = from_cproj_root.find('.//option[@valueType="includePath"]')
        to_option_include_path = to_cproj_root.find('.//option[@valueType="includePath"]')

        insert_h_dir_num = 0
        for child in from_option_include_path:
            to_option_include_path.insert(insert_h_dir_num, child)
            insert_h_dir_num += 1

        ET.indent(to_cproj_tree) # format
        to_cproj_tree.write(cproj_to, encoding='utf-8', xml_declaration=True)


    # 将相应文件插入到 ccs 工程
    def __insert_file_to_ccs(self,ccsproj_path,cproj_path,proj_path,KIND,LIST,GROUP_NAME):
        # cproj_path -> .h 搜索空间在这里配置 
        # proj_path -> .c 通过 URI 增加

        # comp/tal_xxx -> comp
        # tal_xxx -> tal_xxx 
        GROUP_NAME_SPLIT = GROUP_NAME.split('/')
        if GROUP_NAME_SPLIT[0] == 'app_comp':
            GROUP_NAME = 'app/component'
        elif GROUP_NAME_SPLIT[0] == 'app_driver':
            GROUP_NAME = 'app/driver'
        elif GROUP_NAME_SPLIT[0] == 'app_libs':
            GROUP_NAME = 'app/lib'   
        elif GROUP_NAME_SPLIT[0] == 'comp':
            GROUP_NAME = 'tuyaos/tal'
        elif GROUP_NAME_SPLIT[0] == 'tkl':
            GROUP_NAME = 'tuyaos/tkl'
        elif GROUP_NAME_SPLIT[0] == 'libs':
            GROUP_NAME = 'tuyaos/lib'
        elif GROUP_NAME_SPLIT[0] == 'vendor':
            GROUP_NAME = GROUP_NAME_SPLIT[0]+'/'+GROUP_NAME_SPLIT[2]
        else:
            GROUP_NAME = GROUP_NAME_SPLIT[0]

        if KIND == '.c' or KIND == '.lib' or KIND == '.s':
            proj_tree = ET.parse(proj_path)
            proj_root = proj_tree.getroot()

            kind_map = {'.c' : '1', '.lib' : '1', '.s' : '1'}
            linkedResources = proj_root.find("linkedResources")
           
            for file in LIST:
                if file.endswith(KIND):
                    Link = ET.SubElement(linkedResources,'link')
                    LinkName = ET.SubElement(Link, 'name')
                    LinkName.text = file[3:] 
                    LinkType = ET.SubElement(Link, 'type')
                    LinkType.text = kind_map[KIND]
                    LinkURI = ET.SubElement(Link, 'locationURI')
                    LinkURI.text = "PARENT-2-PROJECT_LOC" + file[2:]

            ET.indent(proj_tree) # format
            proj_tree.write(proj_path, encoding='utf-8', xml_declaration=True)

        elif KIND == '.h':
            cproj_tree = ET.parse(cproj_path)
            cproj_root = cproj_tree.getroot()
            
            # 使用 XPath 查找所有 option 元素，其 valueType 属性为 includePath
            option_include_path = cproj_root.find('.//option[@valueType="includePath"]')
            
            for file in LIST:
                # IncludePath = ET.SubElement(option_include_path,'listOptionValue')
                # IncludePath.set('value', "${PARENT-2-PROJECT_LOC}" + file[2:])
                IncludePath = ET.Element('listOptionValue')
                IncludePath.set('value', "${PARENT-2-PROJECT_LOC}" + file[2:])
                # 在索引 self.insert_h_dir_num 位置插入新元素，让默认的在最下面，然后自己的按照顺序
                option_include_path.insert(self.insert_h_dir_num, IncludePath)
                self.insert_h_dir_num += 1

            ET.indent(cproj_tree) # format
            cproj_tree.write(cproj_path, encoding='utf-8', xml_declaration=True)

        else:
            print("KIND INPUT ERROR")
        
    # CCS BUILD
    def __build_ccs(self, project_name, is_lib=False):
        # workspace 需要使用绝对路径
        if is_lib:
            proj_log_abs_path = my_file_get_abs_path_and_formart(".")
        else:
            proj_log_abs_path = my_file_get_abs_path_and_formart("./.log")
        cmd_import = f'ccs-server-cli.bat -workspace {proj_log_abs_path}/{project_name} -application com.ti.ccs.apps.projectImport -ccs.location {proj_log_abs_path}/{project_name}  -ccs.overwrite -ccs.autoImportReferencedProjects true'
        cmd_build = f'ccs-server-cli.bat -workspace {proj_log_abs_path}/{project_name} -application com.ti.ccs.apps.projectBuild  -ccs.locations {proj_log_abs_path}/{project_name} -ccs.configuration Release'
        
        print(f"{self.ccs_path}")
        print('> [cmd_import]:'+cmd_import)
        print('> [cmd_build]:'+cmd_build)
        print('> wait about 2 min ...')
        my_exe_simple(cmd_import,1,self.ccs_path,None)
        my_exe_simple(cmd_build,1,self.ccs_path,None)

        if is_lib == False:
            ret = my_ide_base.tbuild(self)
            return ret
        else:
            return 1
            
        
    
