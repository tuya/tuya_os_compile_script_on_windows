
#### 背景

在 tuya-wind-ide 上，同一个类型的 SDK 的所有支持的 app 都会被拉取下来，但是某些特殊的情况下，某些 app 是某个 vendor 专属的，用户会强行编译，导致出错，很困扰。

基于此诉求，设计了一种 app 可指定支持 vendor 的方法，当当前编译的 app 未指定当前编译所用的 vendor 会直接报错提醒。

</br>

#### 实现方案

```
 M components/my_template/app/build_app.py
```

在 `build_app.py` 中增加 `def get_support_boards(file_path)` 函数，用于从当前编译的 `f"{DEMO_PATH}/tuya_iot.config"` 中提取 `SUPPORT_BOARDS` 数组：

`SUPPORT_BOARDS` 在 `tuya_iot.config` 规则如下：

```
# SUPPORT_BOARDS=["linux","phy6230_adv"]
```
- 前面加 `#` 号
- 后面是个数组
- 独占一行
- 如果不存在或者 `tuya_iot.config` 不存在，都认为全支持（兼容）

