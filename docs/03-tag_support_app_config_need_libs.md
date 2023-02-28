
### 1.目的

基线打的 lib 库，有时候为了基线的覆盖面大，会将将组建打成多个，根据同系列不同参数的芯片情况。

品类和应用在使用时，需要给品类提供可配置的选项，让其只选择一部分库（闭源和非闭源）

即：原来编译品类和应用时搜索所有的 components 和 libs 文件，现在需要品类和应用中加入

</br>

### 2.操作

无

</br>

### 3. 实现

在 front 时：

1）判断品类/应用目录中是否有 `depend.json`，如果没有按照全加载规则进行
2）在 front 中，选取基线的闭源和开源组件时，直接参考 depend.json

```
{
    "base":{
		"libs":[
		    "libtal_bluetooth.a",
		    "libtal_mesh_factory_test.a",
            "libtal_mesh_gatt_ota.a",
            "libtal_nv_flash.a"
		],
        "components":[
            "tal_driver",
            "tal_gpio_test",
            "tal_oled",
            "tal_security",
            "tal_system",
            "tal_utc",
            "tal_util"
        ]
    }
}
```

- 其中 base 表明时对基线的组件按需加载，libs 写需要加载的闭源组建，components 写需要加载的开源组件
- 注意：只要有 depend.json 存在，就会直接完全依赖它


</br>

### 4. 要求

无

