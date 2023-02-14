
### 1.目的

将 IDE 的默认配置放在 `my_exe/my_exe.json` 中，当调用 `my_exe_get_install_path(NAME)` 时，能够做到：

从环境变量中获取对应 IDE 的环境变量
- 1）判断默认的 PATH 是否存在，如果存在，则直接使用，不做任何进一步判断
- 2）使用 KEY 值匹配 TUYAOS_COMPILE_TOOL 环境变量中的所有环境变量，一旦匹配，则认为该环境变量为所需 PATH (KEY，是数组类型，支持个可能的关键词)
- 3）弹出窗口，让用户自己选择安装的路径，我们通过判断是否是需要的 EXE，如果用户选错了，就退出；如果用户选对了，就将该路径保存在 my_exe.json 的 PATH 中

</br>

### 2.操作

无

</br>
### 3. 实现

修改文件：

- M components/my_exe/my_exe.py
- ?? components/my_exe/my_exe.json

`➜  .ide_tool git:(V2.X) ✗ cat components/my_exe/my_exe.json`：

```
{
    "$KEIL_PATH": {
        "PATH": "C:/Keil_v5",
        "EXE": "UV4.exe",
        "KEY": ["UV4"],
        "FATHER": 1,
        "TITLE": "请选择 Keil 的可执行文件 \"UV4.exe\""
    },
    "$CDK_PATH": {
        "PATH": "D:/C-Sky/CDK",
        "EXE": "cdk.exe",
        "KEY": ["CDK"],
        "FATHER": 0,
        "TITLE": "请选择 cdk 的可执行文件 \"cdk.exe\""
    },
    "$KEIL4_PATH": {
        "PATH": "D:/keil 4",
        "EXE": "UV4.exe",
        "KEY": ["UV4"],
        "FATHER": 1,
        "TITLE": "请选择 Keil4 的可执行文件 \"UV4.exe\""
    },
    "$IAR_PATH": {
        "PATH": "D:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3/common/bin",
        "EXE": "IarBuild.exe",
        "KEY": ["ARM 8.40","IAR804"],
        "FATHER": 0,
        "TITLE": "请选择 IAR 的可执行文件 \"IarBuild.exe\""
    },
    "$IAR930_PATH": {
        "PATH": "D:/Program Files (x86)/IAR Systems/Embedded Workbench 8.3/common/bin",
        "EXE": "IarBuild.exe",
        "KEY": ["ARM 9.30","IAR930"],
        "FATHER": 0,
        "TITLE": "请选择 IAR 的可执行文件 \"IarBuild.exe\""
    },
    "$CODEBLOCKS_PATH": {
        "PATH": "C:/Program Files (x86)/CodeBlocks",
        "EXE": "codeblocks.exe",
        "KEY": ["CodeBlocks"],
        "FATHER": 0,
        "TITLE": "请选择 CodeBlocks 的可执行文件 \"codeblocks.exe\""
    }
}
```

- PATH 为默认搜索路径，如果该路径存在，则直接返回
- KEY 为数组，用于在遍历 TUYAOS_COMPILE_TOOL 环境变量时，通过 KEY 关键词判断哪个是所需要的环境变量
- TITLE 为弹出选项框的标题，提醒用户选择对应的 exe 程序
- FATHER：如果为0，表示最终PATH就是所选exe对应的目录，如果为1表示其父目录
- EXE 为弹出选项框，让用户指定自己安装目录的锚定文件（即：当弹出窗口让用户自己选择可执行程序时，如果其名字和 EXE 对不上，则认为选择错误，直接退出）


</br>

### 4. 要求

无

