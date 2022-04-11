#!/usr/bin/env python3
# coding=utf-8
import subprocess

# 执行一个命令，可选阻塞与不阻塞
def my_exe_simple(cmd,wait=0):
    dev = subprocess.Popen(cmd,shell=True,env=None,universal_newlines=True,bufsize=1)
    #dev = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=None,universal_newlines=True,bufsize=1)
    if wait == 1:
        dev.wait()

