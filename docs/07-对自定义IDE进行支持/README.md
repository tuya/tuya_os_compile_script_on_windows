支持用户使用自己的方式编译固件和生成库的 IDE 导入方式，当前目录下提供了一个最简单的 vendor 中的模板文件：

```
➜  templates git:(V2.X) ✗ tree
.
|-- self
|   |-- build.py
|   `-- create_lib.py
`-- vendor.json
```

**当执行编译固件时：** ide_tool 会准备好所有资料（包括 .c .h .lib 等）放入 `.log/self_src.json` 文件，然后调用 `templates` 中的 `build.py`，在 `build.py` 中用户需要实现自己的编译固件的逻辑，然后在 `.log` 中生成 `vendor.json` 中指定的固件名字。

**当执行生成 SDK 时：** ide_tool 会在每个需要打库的组件时调用 `create_lib.py`，调用时会将打库所需要的 .c 和生成的目标路径和名字以参数方式告知。用户需要在  `create_lib.py` 中实现将 .c 打包成库的逻辑，其中库必须放在指定的地方，以指定的名字。