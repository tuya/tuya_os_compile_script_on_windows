# all_in_one_ide_tool


## 一、概述

整个 ide_tool 的设计思想为：

- `my_ide_front` 用于生成项目描述文件 `project.json`
- `my_ide_xxx` 用于根据 `project.json` 生成目标编译平台的工程文件（例如:生成 keil、IAR、makefile 等）

这样能做到：pre-build 生成通用项目描述文件，build 生成兼容不同 IDE 的工程并且具备编译、烧录等功能。

</br>

## 二、预编译
### 2.1 资源框架与资源描述模板


预编译主要使用 `my_ide_front` 脚本，该脚本按照 `sdkconfig.json`、`depend.json`、`tuya_iot.config` 的限制，将 `vendor.json` 拼接组件、库、应用等资源文件生成 `project.json` 项目描述文件。

该 ide_tool 能够处理 **基线、品类、应用**，他们分别涉及的目录如下：

条目 | 路径 | 基线目录 | 品类目录 | 应用目录
---|---|--|---
APP_PATH | PROJECT_PATH+"/"+my_file_path_formart(app_path) | 应用目录 | 应用目录   | 应用目录
APP_COMP_PATH | APP_PATH+"/app.components" 				   | 		 |  		| 应用组件    
APPx_COMP_PATH | PROJECT_PATH+"/application_components"    | 		 | 应用组件   |
APP_DRIVERS_PATH | APP_PATH+"/app.drivers" 				   |  		 | 		    |应用驱动
APPx_DRIVERS_PATH | PROJECT_PATH+"/application_drivers"    | 		 | 应用驱动  |
APP_LIBS_PATH | APP_PATH+"/app.libs" 					   | 		 |			| 应用库
COMP_PATH | PROJECT_PATH+"/components" 					   | 基线组件 | 基线组件（开源）   | 基线组件（开源） 
LIBS_PATH | PROJECT_PATH+"/libs" 						   |  		 | 基线库（闭源组件） | 基线库（闭源组件）
INCLUDE_PATH | PROJECT_PATH+"/include"					   | 基线头文件 | 基线头文件</br>（包括闭源库头文件） | 基线头文件</br>（包括闭源库头文件）
VENDOR_PATH | PROJECT_PATH+'/vendor/'+vendor_name 		   | vendor | vendor | vendor  
VENDOR_JSON | VENDOR_PATH+'/toolchain/templates/vendor.json' | vendor 描述文件 | vendor 描述文件 | vendor 描述文件 
CONFIG_FILE | PROJECT_PATH+"/build/tuya_iot.config" 	   | 工程配置文件 | 工程配置文件 | 工程配置文件
ADAPTER_PATH | PROJECT_PATH+"/adapter"					   | 基线适配层头文件 | 在 include 中 | 在 include 中 
SDK_CONFIG_JSON | APP_PATH+"/sdkconfig.json" 			   | 指定基线开源与闭源组件 | 指定品类开源与闭源组件 | 	
DEPEND_JSON | APP_PATH+"/depend.json" 					   | 指定该应该用使用的组件和库的范围 | same | same
	
</br>

上述资源描述会放入如下 json 模板中：

```Python
json_root={
	'output':{
		'project_path':'$ABS_PROJECT_ROOT',
		'path':OUTPUT_PATH,
		'kind':os.path.basename(os.path.dirname(app_path)),
		'vendor':vendor_name,
		'fw':{
			'name':FIRMWARE_NAME,
			'ver':FIRMWARE_VERSION
		}
	},
	'app':{},
	'app_libs':{},
	'application_components':{},
	'application_drivers':{},
	'libs':{},
	'components':{},
	'include':{},
	'adapter':{},
	'tkl':{
		'drivers':{},
		'system':{},
		'utilities':{},
		'bluetooth':{},
		'security':{},
		'include':{}
	},
}
```

</br>

### 2.2 资源剪裁规则

整个预编译最复杂的部分是资源剪裁（如果没有资源剪裁需求，直接扫描对应文件夹，取出对应的头文件目录和 .c 文件即可）。

ide_tool 总共有三个文件用于剪裁：

条目 | 剪裁策略 
---|---
depend.json | 直接圈死整个工程所使用的 libs 和 库，之后的无论编译还是生成库，都在这个范围内，如果没有该文件，则认为全选
```
{
    "base":{//无论应用、品类、基线都在这里写，脚本会进行名字匹配
        "libs":[
        ],
        "components":[
            "tal_beacon2",
            "tal_xxtea"
        ]
    }
}
``` 
</br>

条目 | 剪裁策略 
---|---
tuya_iot.config | 这个比较复杂，具体参见《docs/01-tag_support_app_package.md》，主要从两个维度对资源进行剪裁：</br> - 通过影响 local.mk，从而对组件内部资源进行剪裁 </br> - 通过产生app_config.h(品类和应用)，来影响代码中的逻辑块 </br></br>备注：基线的 tuya_iot.config(->tuya_iot_config.h) 是在 cde 平台上生成的

文件 | 应用开发 | 基线、品类开发
---|---|---
CONFIG_FILE | `BUILD_PATH+"/tuya_iot.config"` | `BUILD_PATH+"/tuya_iot.config"`
CONFIG_FILE_BK | `APP_PATH+"/build/tuya_app.config"` | `APP_PATH+"/tuya_iot.config"`
KCONFIG_FILE | `BUILD_PATH+"/APPconfig"` | `BUILD_PATH+"/IoTOSconfig"`

</br>

条目 | 剪裁策略 
---|---
sdkconfig.json | 该剪裁主要影响生成 SDK，写在该名单中的意味着要闭源，不在该名单中的意味着开源（整个范围受 depend.json 限制）

```
{
    "sdk":{
		"libs":[
		    "tal_beacon2",
		    "tal_xxtea"
		]
    }
}
```
</br>

### 2.3 资源剪裁实现
#### 2.3.1 depend 和 config 影响编译资源细节

1）my_file_create_subgroup 自带依赖 CONFIG_FILE，因此对于应用层组件直接：

```
 json_root['app'] = my_file_create_subgroup(APP_PATH,CONFIG_FILE)
```

2）组件则相对复杂，需要被 depend.json 限制，因此编写一个函数：

```
def _front_components(ITEM_PATH,JSON_ROOT,KEY,CONFIG_FILE,DEPEND):
```

可以判断是否有 depend.json 做不同的处理：

- 没有：遍历组件目录下所有条目，然后针对每个组件调用 `my_file_create_subgroup`
- 有：遍历 depend 中的描述组件，然后判断给定组件目录下是否有该组件，如果有，调用 `my_file_create_subgroup`

3）同组件处理，lib 处理也编写了一个个函数：

```
def _front_libs(APP_LIBS_PATH,LIBS_PATH,INCLUDE_PATH,JSON_ROOT,DEPEND):
```

逻辑：

- 没有：直接将 APP_LIBS_PATH 和 LIBS_PATH 下的所有库加入，同时将 include 中的所有头文件加入
- 有：遍历 depend 中描述的库，然后判断该库是否在 APP_LIBS_PATH 、LIBS_PATH 下，若在放入对应 list 中进行汇总，同时头文件也计算出来放在 list 中汇总，最后合并到 json_root 中

</br>

#### 2.3.2 depend 和 sdkconfig 影响库输出细则

1）在 `my_ide_base.py` 的 `tmake` 中会从 `project.json` 中拷贝出 `output` 条目：

```Python
'output':{
	'project_path':'$ABS_PROJECT_ROOT',
	'path':OUTPUT_PATH,
	'kind':os.path.basename(os.path.dirname(app_path)),
	'vendor':vendor_name,
	'fw':{
		'name':FIRMWARE_NAME,
		'ver':FIRMWARE_VERSION
	}
}
```
然后根据 `output-kind` 是基线还是非基线（品类/应用），给其增加 `sdk` 描述：

```Python
if self.output['kind'] == 'apps':
	# self.output['sdk'].update({'components':{**load_dict['application_components'],**load_dict['application_drivers']}})
	self.output['sdk'].update({'application_components':load_dict['application_components']})
	self.output['sdk'].update({'application_drivers':load_dict['application_drivers']})
elif self.output['kind'] == 'samples':
	self.output['sdk'].update({'components':load_dict['components']})
else:
	print('error')
```

**因为：** 基线打库只关注 `components` 部分，品类和应用打库只关注 `application_drivers` 和 `application_components` 部分，该 `sdk` 字段保存了将要打库的可选范围（该范围内的库已经在 2.3.1 中被 depend 和 config 影响过了。

</br>

2）为了方便输出基线 SDK，实现了一个函数 `def tBasePackage(self)`，该函数其他部分都是中规中矩的剪裁复制，对于组件部分则借助 `_tlib` 实现。

`_tlib` 会被各个子类 ide 继承实现，实现主要策略如下：遍历 `self.output['sdk']['components']` 的每个组件，判断该组件是否在打库名单中 `self.output['sdk']['libs']`，若在进行打库，若不在形成开源组件

3）同输出基线 SDK，输出应用 SDK 也实现了一个函数 `def tAppPackage(self):`，其策略和输出基线 SDK 一样，只要将范围提前框好 `self.output['sdk']['components']`，将打库白名单框好 `self.output['sdk']['libs']`，和基线不太一样的点是：需要将 `self.output['sdk']['application_components']` 复制给 `self.output['sdk']['components']`打库，然后，清空，再将 `self.output['sdk']['application_drivers']` 复制给 `self.output['sdk']['components']`打库

**备注：** 特殊的，由于 `_tlib` 对开源组件的处理会只提取有用 .c 和 .h，对于基线是这个要求，但是对于应用和品类就需要将 config 带出去。因此在上述 3）中需要在调用 `_tlib` 前，需要提前筛选出 `self.output['sdk']['components']` 中的开源部分，进行特殊提取。



- [01-tag_support_app_package.md](./docs/01-tag_support_app_package.md)
- [02-tag_my_exe_get_install_path.md](./docs/02-tag_my_exe_get_install_path.md)
- [03-tag_support_app_config_need_libs.md](./docs/03-tag_support_app_config_need_libs.md)
- [04-tag_support_after_make_call_user_python_scripts.md](./docs/04-tag_support_after_make_call_user_python_scripts.md)


