#!/usr/bin/env python
# coding=utf-8
import json
import os
import sys

my_ide_base_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(my_ide_base_file_dir+'/../components')
from my_file.my_file import *
from my_exe.my_exe import my_exe_simple, my_exe_get_install_path

class my_ide_base(object):
    json_file = ""
    __log_path = '.log'
    
    src = {'c_files':[],'h_dirs':[],'l_files':[],'s_files':[],
           'h_dir_str':'','l_files_str':'','l_dirs_str':''}
    output = {}
    flash = {}
    cmd = {}
    var_map = {}

    # 初始化
    def __init__(self,JSON_FILE):
        self.json_file = JSON_FILE
        print(JSON_FILE)
        
    # make
    def tmake(self,offset='.'):
        print('\nMAKE')
        print('> clean .log \n> copy json_file to .log')
        my_file_clear_folder(self.__log_path)
        my_file_copy_files_to([self.json_file],self.__log_path)
        self.json_file = self.__log_path+'/'+os.path.basename(self.json_file)
        my_file_str_replace(self.json_file,'$PROJECT_ROOT',offset)#PROJECT_PATH
        
        with open(self.json_file,'r') as load_f:
            load_dict = json.load(load_f)
           
            print('#1. fill the output dict')
            tool = load_dict['tool'][self.ide_kind]
            self.output = load_dict['output']
            self.output['sdk'].update({'components':load_dict['components']})
            self.output['fw'].update({'output':tool['output']})
            
            print('#2. fill the cmd dict')
            self.cmd = {**tool['toolchain'], **tool['cmd']}
            
            print('#3. fill flash cmd dict')
            self.flash['bin_path'] =  my_file_get_abs_path_and_formart(tool['flash']['bin_path'])
            self.flash['flash_user_cmd'] =  tool['flash']['flash_user_cmd']
            self.flash['flash_all_cmd'] =   tool['flash']['flash_all_cmd']
            
            print('#4. fill the src dict')
            self.__json_deep_search(load_dict)
            
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
                    
            print('#5. get var map')
            self.__get_variable_map()
            
    # 编译
    def tbuild(self):
        print('> build end, create final fw...')
        # 编译结束，产生最终固件产物
        output_path = self.output['path']
        my_file_clear_folder(output_path)
        
        DEMO_NAME = self.output['fw']['name']
        DEMO_FIRMWARE_VERSION =  self.output['fw']['ver']
                
        for k in self.output['fw']['output']:
            fw = './.log/'+self.output['fw']['output'][k]
            print('copy %s -> %s' %(fw,k))
            if os.path.exists(fw):
                suffix = os.path.splitext(os.path.basename(fw))[1]
                shutil.copy(fw, output_path+'/'+DEMO_NAME+'_'+k+'_'+DEMO_FIRMWARE_VERSION+suffix)
                if k == 'UA':
                    shutil.copy(fw, output_path+'/'+DEMO_NAME+'_'+DEMO_FIRMWARE_VERSION+suffix)
            else:
                print('> build fail')
                return 0
                
        print('> build success')
        return 1
      
    # 形成 SDK
    def tsdk(self):
        print('\nMAKE')
        my_file_clear_folder(self.output['path']) 
        
        print('#1. Create Output Package...')
        template_dir    = my_ide_base_file_dir+'/../../template'
        
        output_path     = self.output['path']
        vendor_name     = self.output['vendor']
        app_path        = output_path + '/apps'
        comp_path       = output_path + '/components'
        docs_path       = output_path + '/docs'
        incs_path       = output_path + '/include'
        libs_path       = output_path + '/libs'
        scripts_path    = output_path + '/scripts'
        tools_path      = output_path + '/tools'
        vendor_path     = output_path + '/vendor'
    
        project_root = self.output['project_path']
        docs_root    = project_root+'/docs'
        include_root = project_root+'/include'
        adapter_root = project_root+'/adapter'
        vendor_root  = project_root+'/vendor'
        
        my_file_clear_folder(app_path)
        my_file_clear_folder(comp_path)
        my_file_copy_dir_to(docs_root,docs_path)
        my_file_copy_dir_to(include_root,incs_path)
        my_file_clear_folder(libs_path)
        my_file_clear_folder(scripts_path)
        my_file_clear_folder(tools_path)
        my_file_copy_dir_to(vendor_root+'/'+vendor_name,vendor_path+'/'+vendor_name)
        
        # 删除 toolchain/software 中的解压之后的文件，让 SDK 小一些
        software_path = vendor_path+'/'+vendor_name+'/toolchain/software/'
        unzip_dir = my_file_find_subdir_in_path(software_path)
        for subdir in unzip_dir:
            my_file_rm_dir(software_path+subdir)
        
        my_file_copy_files_to([project_root+'/CHANGELOG.md',
                               project_root+'/LICENSE',
                               project_root+'/README.md',
                               project_root+'/RELEASE.md',
                               template_dir+'/sdk/build_app.py'],output_path)
        my_file_copy_files_to([template_dir+'/sdk/pre_build.py'],scripts_path)
    
        print('#2. Create include/base  include/vendor/adapter...')        
        adapters = my_file_find_subdir_in_path(adapter_root)
        for adapter in adapters:
            src_path = adapter_root+'/'+adapter+'/include'
            dst_path = incs_path+'/vendor/adapter/'+adapter+'/include'
            my_file_copy_dir_to(src_path,dst_path)
            print('    [cp] cp %s to %s'%(src_path,dst_path))
            
        print('#3. use _tlib to greate the libs ...')   
        self._tlib(libs_path,incs_path,comp_path,self.__log_path)
    
    # 形成 SDK 中用库的函数
    def _tlib(self,libs_path,incs_path,comp_path,log_path):
        print('#4. Create libs...')
       
    # 烧录
    def tflash(self,OP):
        flash_evn = self.flash['bin_path'];
        
        if OP == 'flash_user':
            cmd = self.flash['flash_user_cmd']
            print("\n[flash] flash user: %s\n"%(cmd))
            my_exe_simple(cmd,1,flash_evn,self.var_map)
        if OP == 'flash_all': 
            cmd = self.flash['flash_all_cmd']
            print("\n[flash] flash all: %s\n"%(cmd))        
            my_exe_simple(cmd,1,flash_evn,self.var_map)    
    
    #######################################################################
    # 其它函数
    #######################################################################
    
    # 深度优先遍历时，用来统计.c .h .s .lib 的文件信息
    # 或者直接以这些信息插入到 keil 等工程文件中
    def _create_subgroup(self,KIND,LIST,GROUP_NAME):
        if len(LIST) == 0:
            return
            
        if KIND == '.c':
            self.src['c_files'] += LIST
        elif KIND == '.h':
            self.src['h_dirs'] += LIST
        elif KIND == '.s':
            self.src['s_files'] += LIST
        elif KIND == '.lib':
            self.src['l_files'] += LIST
        #else:            
            #print(area[k])
    
    def __json_deep_search(self, area, group_name='', i=0):
        for k in area:
            #print('----' * i, k, sep='')
            if  isinstance(area[k],dict):
                old_group_name = group_name
                if group_name == '':
                    if k == 'output' or k == 'tool':
                        continue
                    elif k == 'components':
                        group_name = 'comp'
                    else:
                        group_name = k
                else:
                    group_name = group_name+'/'+k
                    
                self.__json_deep_search(area[k], group_name, i+1)
                group_name = old_group_name
            else:
                if k == "c_files":
                    self._create_subgroup('.c',area[k],group_name)
                elif k == "h_dir":
                    self._create_subgroup('.h',area[k],group_name+'/h')
                elif k == "s_files":
                    self._create_subgroup('.s',area[k],group_name+'/s')
                elif k == "l_files":
                    self._create_subgroup('.lib',area[k],group_name+'/libs')
                #else:            
                    #print(area[k])
                    
    # 获取变量映射，用于替换 tool 中的变量
    def __get_variable_map(self):
        # Get the path to the current python interpreter
        PYTHON_PATH = sys.executable
        
        # Get the keil path
        EXE_USED_MAP = my_file_str_list_count(self.json_file,['$KEIL_PATH'])
        #print(EXE_USED_MAP)
        for key in EXE_USED_MAP:
            if EXE_USED_MAP[key] == 0:
                EXE_USED_MAP[key] = ""
            else:
                EXE_USED_MAP[key] = my_exe_get_install_path(key)
           
        # FW
        output_path = self.output['path']
        DEMO_NAME = self.output['fw']['name']
        DEMO_FIRMWARE_VERSION =  self.output['fw']['ver']
        
        UA_SUFFIX = os.path.splitext(os.path.basename(self.output['fw']['output']['UA']))[1]
        PROD_SUFFIX = os.path.splitext(os.path.basename(self.output['fw']['output']['PROD']))[1]
        
        FW_UA = output_path+'/'+DEMO_NAME+'_UA_'+DEMO_FIRMWARE_VERSION+UA_SUFFIX
        FW_PROD = output_path+'/'+DEMO_NAME+'_PROD_'+DEMO_FIRMWARE_VERSION+PROD_SUFFIX
        
        self.var_map = {
            '$OUTPUT':self.__log_path,
            '$O_FILES':'',
            '$L_FILES':' '.join(self.src['l_files']),
            '$LIB_DIRS':self.src['l_dirs_str'],
            '$LIBS':self.src['l_files_str'],
            '$MAP':self.__log_path+'/output.map',
            '$ELF':self.__log_path+'/output.elf',
            '$LST':self.__log_path+'/output.lst',
            '$PYTHON':PYTHON_PATH,
            '$KEIL_PATH':EXE_USED_MAP['$KEIL_PATH'],

            '$UA':FW_UA,
            '$PROD':FW_PROD
        }      
        
        my_file_save_json(self.__log_path+'/var_map.json',self.var_map)
       
