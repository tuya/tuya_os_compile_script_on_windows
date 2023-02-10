# coding:utf-8
import os
import sys
import shutil
import subprocess

from pathlib import Path

# Parameter description:
# $1 - Demo path: apps\tuyaos_demo_ble_peripheral
# $2 - Demo name: tuyaos_demo_ble_peripheral
# $3 - Demo firmware version: 1.0.0
# $4 - Demo command: build/clean/flash_all/flash_app
# $5 - 产物包路径，如： output/dist/product1_1.0.0
# python build_app.py apps\tuyaos_demo_ble_peripheral tuyaos_demo_ble_peripheral 1.0.0 clean

print(len(sys.argv))
if len(sys.argv) < 4:
    print("Script parameter error !!!")

DEMO_PATH = sys.argv[1].replace('\\','/')
DEMO_NAME = sys.argv[2].replace('\\','/')
DEMO_FIRMWARE_VERSION = sys.argv[3]
DEMO_OUTPUT_PATH = "_output"

BUILD_COMMAND = 'build'
PARAMS1 = 'NONE'

if len(sys.argv) == 5:
    BUILD_COMMAND = sys.argv[4]
if len(sys.argv) == 6:
    BUILD_COMMAND = sys.argv[4]
    DEMO_OUTPUT_PATH = sys.argv[5] 
    PARAMS1 = sys.argv[5]


def get_board_name(path):
    for root, dirs, files in os.walk(path):
        return dirs[0]
BOARD_NAME = get_board_name('./vendor')

print("DEMO_PATH: " + DEMO_PATH)
print("DEMO_NAME: " + DEMO_NAME)
print("DEMO_FIRMWARE_VERSION: " + DEMO_FIRMWARE_VERSION)
print("BOARD_NAME: " + BOARD_NAME)
print("BUILD_COMMAND: " + BUILD_COMMAND)

PYTHON_PATH     = '"'+sys.executable+'"'
SCRIPT_IDE_TOOL = PYTHON_PATH + ' ./.ide_tool/ide_tool.py'
SCRIPT_PREPARE  = PYTHON_PATH + ' ./vendor/'+BOARD_NAME+'/prepare.py'

# 删除一个文件夹
def rm_dir(path):
    def readonly_handler(func, path, execinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if os.path.exists(path):
        shutil.rmtree(path, onerror=readonly_handler)


def exe(note,cmd):
    print(note)
    ret = subprocess.call(cmd,shell=True)
    if ret != 0:
        print("execution failed !!!")
        sys.exit(1)

if BUILD_COMMAND == "config":
    CONFIG_AUTO = 0
    if PARAMS1 == 'gui':
        ENABLE_GUI = 0
    else:
        ENABLE_GUI = 1
    cmd = "%s menuconfig \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" %d %d"%(SCRIPT_IDE_TOOL, './', DEMO_PATH, DEMO_NAME, DEMO_FIRMWARE_VERSION, BOARD_NAME, CONFIG_AUTO, ENABLE_GUI)
    exe("config...", cmd)

if BUILD_COMMAND == "build":
    cmd = "%s pr-build \"%s\" \"%s\" \"%s\" \"%s\" \"%s\""%(SCRIPT_PREPARE, DEMO_PATH,BOARD_NAME,DEMO_OUTPUT_PATH,DEMO_NAME,DEMO_FIRMWARE_VERSION)
    exe("build-pre...", cmd)
        
    cmd = "%s build"%(SCRIPT_PREPARE)
    exe("build...", cmd)

if BUILD_COMMAND == "sdk":
    cmd = "%s sdk"%(SCRIPT_PREPARE)
    exe("build...", cmd)

if BUILD_COMMAND == "flash_user":
    cmd = "%s flash_user"%(SCRIPT_PREPARE)
    exe("flash user...", cmd) 

if BUILD_COMMAND == "flash_all":
    cmd = "%s flash_all"%(SCRIPT_PREPARE)
    exe("flash all...", cmd)
    
if BUILD_COMMAND == "clean":
    print("clean...")
    rm_dir('.log')
