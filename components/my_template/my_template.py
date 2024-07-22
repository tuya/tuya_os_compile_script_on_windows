#!/usr/bin/env python3
# coding=utf-8
import json
import os
import sys
import filecmp

my_template_dir = os.path.dirname(__file__)  
sys.path.append('..')
from my_file.my_file import *


class my_template():
    __project_path = ''

    def __init__(self,PROJECT_PATH):
        self.__project_path = my_file_path_formart(PROJECT_PATH)

    def __get_all_files(self,path):
        for root, dirs, files in os.walk(path):
            return files

    def __modify_prepare_files(self):
        vendor_path = os.path.join(self.__project_path, "vendor")
        for root, dirs, files in os.walk(vendor_path):
            # 只处理一级目录
            if root == vendor_path:
                for dir_name in dirs:
                    prepare_file = os.path.join(vendor_path, dir_name, "prepare.py")
                    if os.path.exists(prepare_file):
                        self.__modify_url(prepare_file)

    def __modify_url(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk') as file:
                content = file.read()

        from_url = 'https://github.com/nbtool/all_in_one_ide_tool.git' 
        to_url = 'https://github.com/tuya/tuya_os_compile_script_on_windows.git'
        if from_url in content:
            # 修改内容
            new_content = content.replace(from_url, to_url) 

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f">> Modified URL: {file_path}, {from_url}->{to_url}")

    def check(self):
        # 兼容老的情况，通过判断 scripts 中是否有 prepare.py 来判别
        if os.path.exists(self.__project_path+'/scripts/pre_build.py'):
            print('\nSYN NO TEMPLATE------------------------')
            return

        FILES_APP = self.__get_all_files(my_template_dir+'/app')
        FILES_SDK = self.__get_all_files(my_template_dir+'/sdk')
        FILES_CUR = self.__get_all_files(self.__project_path)

        #print(FILES_APP)
        #print(FILES_SDK)
        #print(FILES_CUR)

        FILES = []
        KIND = ''
        if 'build_app.py' in FILES_CUR:
            FILES = FILES_APP
            KIND = 'app'
        else:
            FILES = FILES_SDK
            KIND = 'sdk'

        print('\nSYN ' + KIND + ' TEMPLATE------------------------')
        print('Compare Some Files With Template:')
        print('>>',FILES)
        for file in FILES:
            file_a = self.__project_path + '/' + file
            file_b = my_template_dir + '/' + KIND + '/' + file
            if os.path.exists(file_a):
                result = filecmp.cmp(file_a,file_b)
            else:
                result = False

            if result:
                print('-> [Y] ' + file + ' is same')
            else:
                print('-> [N] ' + file + ' is not same')
                print('\t-> execute: copy ' + file_b + ' to ' + file_a)
                my_file_copy_file_to_file(file_b,file_a)
        
        print('\nChange URL:------------------------')       
        self.__modify_prepare_files()
