#!/usr/bin/env python
# coding=utf-8
import sys,json
 
# 需要编译的各种文件信息全部放在 SELF_SRC_JSON_FILE 文件中，方便用户自行后续处理
SELF_SRC_JSON_FILE = sys.argv[1]
print(f"SELF_SRC_JSON_FILE={SELF_SRC_JSON_FILE}")
with open(SELF_SRC_JSON_FILE, 'r', encoding='utf-8') as file:
	self_src = json.load(file)
	#print(self_src)

# 自己在这里实现编译生成固件

# 模拟生成了一个固件
hex_file = './.log/output.exe'
with open(hex_file, 'w') as file:
    pass
print(f"固件 {hex_file} 生成成功...")






