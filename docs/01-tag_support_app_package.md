
### 1.目的

用于支持应用品类打包

</br>

### 2.操作

在品类工程根目录下运行：

```shell
# 编译生成固件
python build_app.py ./apps/tuyaos_mesh_module_common_tlsr825x tuyaos_mesh_module_common_tlsr825x  6.0     

# 对应用进行打包
python vendor/tlsr825x_smesh/prepare.py 'sdk' 
```

最终会在 _output 目录下生成应用打包文件夹：

```
➜  tuyaos_mesh_module_common_tlsr825x git:(master) ✗ tree -L 3
.
├── app.components         # 直接开源的组件（这些组件从源组件去除 .git 直接对外）
│   ├── app_mesh_module
│   │   ├── include
│   │   ├── IoTOSconfig
│   │   ├── local.mk
│   │   ├── README.md
│   │   └── src
│   ├── app_tuya_driver
│   │   ├── include
│   │   └── src
│   ├── tbs_storage_ib
│   │   ├── include
│   │   ├── IoTOSconfig
│   │   ├── local.mk
│   │   ├── README.md
│   │   └── src
│   └── tfm_mesh_local_auto
│       ├── include
│       ├── local.mk
│       ├── README.md
│       └── src
├── app.libs            # 闭源组件（这些组件打包成库，然后对外）
│   ├── include
│   │   └── components
│   └── src
│       ├── libtbl_mesh_uart_protocol.a
│       └── libtbs_fifo.a
├── build               # 默认的 kconfig 配置文件
│   └── tuya_app.config
├── doc                 # 原 APP 文件
├── include             # 原 APP 的 include 文件
├── IoTOSconfig         # 原 APP 的 IoTOSconfig 文件
├── local.mk            # 原 APP 文件
├── README.md           # 原 APP 文件
└── src                 # 原 APP 的 src 文件
```

</br>
### 3. 实现

修改文件：

-  M components/my_ide/my_ide_front.py
-  M components/my_kconfig/my_kconfig.py
-  M components/my_ide/my_ide_base.py
-  M components/my_template/app/build_app.py
- ?? components/my_template/app/ci_autopack.sh

**A -> ** 在 ide_front 中，新增 `app.components` 和 `app.libs`, 用于对打包后的应用进行编译，由于打包后的应用中除了包含其自身的 `src` 和 `include`，还有闭源和开源库，因此其应用代码里必须有一个 local.mk 用于指明应用的 .c 和 .h 文件，否则会将组件也自动搜索进 `app`。(该 local.mk 别忘了将当前应用的根目录加上，因为 app_config.h 在应用根目录）

**B -> ** 在 my_kconfig 中，为了兼容 tuya wind 自带的 KCONFIG GUI，因此 `my_kconfig` 多加一个 `gui` 是否使能的参数。当其为 1 时，启动 terminal gui，当其为 0 时，仅仅是生成 KCONFIG 文件，然后让 wind ide 的 GUI 读取 KCONFIG 文件，加载页面。

此外，由于基线开发、品类开发的 KCONFIG 文件、config_bk 文件和应用开发时不一样，因此通过 `if os.path.exists(APP_PATH+'/build')` 做计算区分：

文件 | 应用开发 | 基线、品类开发
---|---|---
CONFIG_FILE | `BUILD_PATH+"/tuya_iot.config"` | `BUILD_PATH+"/tuya_iot.config"`
CONFIG_FILE_BK | `APP_PATH+"/build/tuya_app.config"` | `APP_PATH+"/tuya_iot.config"`
KCONFIG_FILE | `BUILD_PATH+"/APPconfig"` | `BUILD_PATH+"/IoTOSconfig"`

这几个文件具体关系为：

- 当 auto = 0 时，遍历所有组件的 IoTOSconfig + 应用的 IoTOSconfig，合成一个工程级别的 KCONFIG_FILE。
	- 如果 gui = 1，会调用 terminal gui，展示 kconfigmenu，用户配置完毕后，会生成 CONFIG_FILE，同时进行一次备份 CONFIG_FILE_BK，并且在此时会根据 CONFIG_FILE 生成 `APP_PATH+"/app_config.h"`
	- 如果 gui = 0，会到此结束，之后 wind ide kconfig gui 会读取 KCONFIG_FILE，让用户配置，之后会生成 `APP_PATH+"/build/tuya_app.config"` 

- 当 auto = 1 时，判断是否存在 CONFIG_FILE_BK
	- 存在：拷贝 CONFIG_FILE_BK to KCONFIG_FILE，然后生成 `APP_PATH+"/app_config.h"`
	- 不存在：运行 `my_kconfig(project_path,app_path,fw_name,fw_version,board_name,0,gui)`

**C -> ** 在 my_ide_base 中，由于我们想要将基线、品类打包复用同一个命令 'sdk'，因此我们在 `tsdk` 中通过判断是基线还是品类，调用不同的函数。

给品类打包使用 `tAppPackage` 函数，该函数和 `tBasePackage` 类似，最大的区别是：给应用组件打库的时候，需要从全部组件中剔除 tal 组件（基线组件），然后对于开源应用组件直接复制去除 .git 开源，对于闭源组件，打库。（基线的开源组件，是只释放默认配置的对应的 .c .h 不会全部开放）

**D -> ** build_app 修改一行代码，支持 sdk 命令；ci_autopack 用于应用打包的通用模板脚本，CI 平台打包命令如下：

```shell
sh -c "./ci_autopack.sh 'apps/tuyaos_mesh_module_common_tlsr825x' 'tuyaos_mesh_module_common_tlsr825x' '0.0.7' 'output/dist/package_tuyaos_mesh_module_common_tlsr825x_0.0.7.tar.gz' 'tuyaos_mesh_module_common_tlsr825x'"
```

</br>

### 4. 要求
#### 4.1 对品类 app 的要求

待打包的品类 app 需要有：doc、include、src、README.md、IoTOSconfig、local.mk，其中 local.mk 和其他通用 local.mk 有一点区别：

> `LOCAL_TUYA_SDK_INC := $(LOCAL_PATH)/include $(LOCAL_PATH)`

```makefile
# 当前文件所在目录
LOCAL_PATH := $(call my-dir)

#---------------------------------------

# 清除 LOCAL_xxx 变量
include $(CLEAR_VARS)

# 当前模块名
LOCAL_MODULE := $(notdir $(LOCAL_PATH))

# 模块对外头文件（只能是目录）
# 加载至CFLAGS中提供给其他组件使用；打包进SDK产物中；
LOCAL_TUYA_SDK_INC := $(LOCAL_PATH)/include $(LOCAL_PATH)    #<-- 注意要加上 $(LOCAL_PATH)

# 模块对外CFLAGS：其他组件编译时可感知到
LOCAL_TUYA_SDK_CFLAGS :=

# 模块源代码
LOCAL_SRC_FILES := $(foreach dir, $(LOCAL_PATH)/src, $(wildcard $(dir)/*.c))     #<-- 千万不能用 shell find 去查，不然 windows 不兼容

# 模块内部CFLAGS：仅供本组件使用
LOCAL_CFLAGS :=

# 全局变量赋值
TUYA_SDK_INC += $(LOCAL_TUYA_SDK_INC)  # 此行勿修改
TUYA_SDK_CFLAGS += $(LOCAL_TUYA_SDK_CFLAGS)  # 此行勿修改

# 生成静态库
include $(BUILD_STATIC_LIBRARY)

# 生成动态库
include $(BUILD_SHARED_LIBRARY)

# 导出编译详情
include $(OUT_COMPILE_INFO)

#---------------------------------------
```

</br>

#### 4.2 对 wind ide 的要求

点击 config 时，首先调用：

```shell
python build_app.py ./apps/tuyaos_mesh_module_common_tlsr825x tuyaos_mesh_module_common_tlsr825x  6.0 config gui
```

该程序执行完会生成 `./build/AppConfig`，wind ide 加载该文件，弹出工程配置文件，用户保存后，生成 `./apps/tuyaos_mesh_module_common_tlsr825x/build/tuya_app.config` (应用能保证有 build 文件夹)





