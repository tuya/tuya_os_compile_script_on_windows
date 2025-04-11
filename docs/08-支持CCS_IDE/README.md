CCS 是 TI 最新的专用 IDE，这里对其进行支持，同级目录放了一个 CCS 导入模板：

```
➜  templates git:(V2.X) ✗ tree -a
.
|-- ccs
|   |-- app_project
|   |   |-- .ccsproject
|   |   |-- .cproject
|   |   |-- .project
|   |   |-- TuyaOS_CC2340.syscfg
|   |   |-- cc23x0_app_freertos.cmd
|   |   |-- main_freertos.c
|   |   `-- run.sh
|   `-- lib_project
|       |-- .ccsproject
|       |-- .cproject
|       `-- .project
`-- vendor.json
```

其中 `app_project` 是编译应用的模板、`lib_project` 是编译 lib 的模板，主要实现逻辑在：`components/my_ide/my_ide_ccs.py` 中。

**PS：**

- 其 .c、.lib 的导入一样，均采用 URI 链接的方式导入工程文件，然后调用 import 命令导入工程，CCS 会自动创建一堆 makefile，之后调用 CCS 的 build 会执行这些 makefile 然后编译。其中 .h 的搜索路径类似 keil，需要加入到 .cproject 中。
- 之前的生成库的工程是在应用工程基础上雕刻的，这里发现 CCS 的生成库的工程和应用很不一样，因此这里采用双工程模板的设计，对于插入 .c、.lib 同应用的插入，对于编译库所需要的头文件搜索目录，直接从应用工程中复制出来，插入 lib 工程。

额外的，在 `components/my_exe/my_exe.json` 对 CCS 进行搜索支持（意味着如果创建环境变量，KEY 是 TI_CCS，值是 "C:/ti/ccs2010/ccs/eclipse"：

```
"$CCS_PATH": {
	"PATH": "C:/ti/ccs2010/ccs/eclipse",
	"EXE": "ccs-server-cli.sh",
	"KEY": [
		"TI_CCS"
	],
	"FATHER": 0,
	"TITLE": "请选择 ti->ccs->eclipse 的可执行文件 \"ccs-server-cli.sh\""
}
```

此外，如果某个 vendor 想要使用 CCS，需要在 prepare.py 中将 IDE_KIND = 'ccs'。
