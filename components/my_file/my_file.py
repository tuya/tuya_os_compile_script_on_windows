#!/usr/bin/env python3
# coding=utf-8
import os
import json
import shutil
import time

# 清空一个文件夹（如果已经存在，则删除）
def my_file_clear_folder(path):
    """
    clear specified folder
    :param path: the path where need to clear.
    :return:
    """
    if os.path.exists(path):
        shutil.rmtree(path, onerror=readonly_handler)

    time.sleep(1)
    os.mkdir(path)

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
        fp_out.write(json.dumps(json_root, sort_keys=True, indent=4, separators=(',', ': ')))
        fp_out.close()
        
# 将 json_root 字典，保存为 json 文件
def my_file_save_json(json_file, json_root):
    with open(json_file,'w') as fp2:
        fp2.write(json.dumps(json_root, sort_keys=True, indent=4, separators=(',', ': ')))
        fp2.close()
    
# 传入一个目录，输出一个字典，包含{ .h 路径; .c; .lib}
# 如果该目录下本来就有 subdir.json，则用这个里面的
def my_file_create_subgroup(SOURCES_ROOT):
    h_list=[]
    c_list=[]
    l_list=[]
    ret=""

    if os.path.exists(SOURCES_ROOT+'/subdir.json') == True:
        with open(SOURCES_ROOT+'/subdir.json','r') as fp:
            content = fp.read()
            if content != "":
                ret = json.loads(content)  #json.loads读的是字符串，必须把文件先读出来

        fp.close()
    else:
        for root, dirs, files in os.walk(SOURCES_ROOT):
            for file in files:
                my_root = root.replace('..','$PROJECT_ROOT')
                if file.endswith(".h"):
                    h_list.append(my_root)
                elif file.endswith(".c"):
                    c_list.append(my_root+"/"+file)
                elif file.endswith(".a"):
                    l_list.append(my_root+"/"+file) 

        ret = {'c_files':c_list,'h_dir':h_list,'l_files':l_list}

    return ret


