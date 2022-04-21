#!/usr/bin/env python3
# coding=utf-8
import os
import json
import shutil
import time
import sys

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir+'/../components')
from my_exe.my_exe import *

# 将数组files中的所有文件复制到目标目录中
# 如果目录不存在，则创建目录
def my_file_copy_files_to(files,dst_path):
    if os.path.exists(dst_path) == False:
        my_file_clear_folder(dst_path)

    for file in files:
        shutil.copy(file,dst_path)

# 将src_paths 数组中所有满足条件的某一类文件，复制到目标目录
# 如果目录不存在，创建目录
def my_file_copy_one_kind_files_to(src_paths,kind,dst_path):
    files = my_file_find_files_in_paths(src_paths,kind)
    my_file_copy_files_to(files,dst_path)


# 将一个目录复制到另一个目录，如果另一个目录已经存在，则删除之
def my_file_copy_dir_to(from_path,dst_path):
    my_file_rm_dir(dst_path) 
    shutil.copytree(from_path,dst_path)

# 查找 path数组中的所有路径下的某种类型的文件
def my_file_find_files_in_paths(paths,kind):
    ret = []
    for path in paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(kind):
                    ret.append(root+'/'+file)

    return ret
                
def my_file_find_subdir_in_path(path):
    for root, dirs, files in os.walk(path):
        return dirs 

# 清空一个文件夹（如果已经存在，则删除）
def my_file_clear_folder(path):
    my_file_rm_dir(path)

    time.sleep(1)
    os.makedirs(path)

# 删除一个文件夹
def my_file_rm_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path, onerror=readonly_handler)

def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


# 将文件中的一个老的字符串替换为新的
def my_file_str_replace(file,old,new):
    rep = ''
    with open(file,'r') as fp:
        contents = fp.read()
        rep = contents.replace(old,new)
        fp.close()
        
    with open(file,'w') as fp2:
        fp2.write(rep)
        fp2.close()

# 合并 json_files 中的所有 json，保存在 json_file_out
def my_file_mege_json(json_files,json_file_out):
    json_root={}
    for json_file in json_files:
        with open(json_file,'r') as fp:
            c = json.load(fp)
            json_root = {**json_root,**c}
            fp.close()

    with open(json_file_out,'w') as fp_out:
        fp_out.write(json.dumps(json_root, sort_keys=False, indent=4, separators=(',', ': ')))
        fp_out.close()
        
# 读取 json_file 返回字典
def my_file_read_json(json_file):
    if os.path.exists(json_file) == False:
        return {}

    with open(json_file,'r') as fp:
        c = json.load(fp)
        fp.close()
        return c

# 将 json_root 字典，保存为 json 文件
def my_file_save_json(json_file, json_root):
    with open(json_file,'w') as fp2:
        fp2.write(json.dumps(json_root, sort_keys=False, indent=4, separators=(',', ': ')))
        fp2.close()
    
# 传入一个目录，输出一个字典，包含{ .h 路径; .c; .lib}
# 如果该目录下本来就有 subdir.json，则用这个里面的
# 如果该目录下本来就有 subdir.mk， 则用 kconfig
# 如果过滤为空，则全部都加
def my_file_create_subgroup(SOURCES_ROOT,CONFIG_FILE="",filter=""):
    h_list=[]
    c_list=[]
    l_list=[]
    ret={}

    if os.path.exists(SOURCES_ROOT+'/subdir.json') == True:
        with open(SOURCES_ROOT+'/subdir.json','r') as fp:
            content = fp.read()
            if content != "":
                ret = json.loads(content)  #json.loads读的是字符串，必须把文件先读出来

        fp.close()

    elif os.path.exists(SOURCES_ROOT+'/local.mk') == True: 
        cmd = "make kconfig LOCAL_PATH=\"%s\" CONFIG=\"%s\" -f %s/makefile"%(SOURCES_ROOT, CONFIG_FILE,current_file_dir) 
        my_exe_simple(cmd,1)       
        if os.path.exists(SOURCES_ROOT+"/subdir.json"):
            ret = my_file_create_subgroup(SOURCES_ROOT)
            os.remove(SOURCES_ROOT+"/subdir.json")                 
    else:
        for root, dirs, files in os.walk(SOURCES_ROOT):
            for file in files:
                my_root = root.replace('..','$PROJECT_ROOT')
                if filter == "":
                    if file.endswith(".h"):
                        h_list.append(my_root)
                    elif file.endswith(".c"):
                        c_list.append(my_root+"/"+file)
                    elif file.endswith(".a"):
                        l_list.append(my_root+"/"+file) 
                elif filter == ".h":
                    if file.endswith(".h"):
                        h_list.append(my_root)

        ret = {'c_files':c_list,'h_dir':h_list,'l_files':l_list}

    return ret

def my_file_get_abs_path_and_formart(relative_path):
    return os.path.abspath(os.getcwd()+'/'+relative_path).replace('\\','/')

def my_file_path_formart(path_str):
    if path_str.endswith('/'):
        path_str = path_str[:-1]
    if path_str.startswith('./'):
        path_str = path_str[2:]
    return path_str

