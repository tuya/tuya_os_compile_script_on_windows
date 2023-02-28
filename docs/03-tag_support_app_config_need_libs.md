
### 1.目的

基线打的 lib 库，有时候为了基线的覆盖面大，会将将组建打成多个，根据同系列不同参数的芯片情况。

品类和应用在使用时，需要给品类提供可配置的选项，让其只选择一部分库（闭源和非闭源）

即：原来编译品类和应用时搜索所有的 components 和 libs 文件，现在需要品类和应用中加入

</br>

### 2.操作

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

### 3. 实现

修改了 `my_ide_front.py`:

通过判断是否存在 `depend.json` 文件 `DEPEND_JSON=APP_PATH+"/depend.json"`，如果不存在，还是走老一套，如果存在：

- 根据 `depend['base']['components']` 加载基线开源组件
- 根据 `depend['base']['libs']` 加载基线闭源库

注意：由于之前可以直接加载整个 `include` 下的头文件（包括 base,vendor,compenents）,其中 compenents 下是所有基线闭源库对应的头文件，有可能会有相同冲突的头文件，因此，当有 `depend.json` 时，会分别加载 `include/vendor`、`include/base` 以及根据依赖的 `lib` 计算出库对应头文件放在路径，然后加载。


```c
    # 按需加载基线的开源与闭源组件<docs/03-xxx>
    depend = my_file_read_json(DEPEND_JSON)
    if depend == {}:
        # 根目录中的 components（一般是基线的开源组件，品类在 cde 上配置在老的组件列，也会放在这里，这种方式已经渐渐弃用了）
        print('    -> components')
        components_list=[]
        for root, dirs, files in os.walk(COMP_PATH):
            components_list = dirs
            break

        for component in components_list:
            print('        -> '+component)
            json_root['components'][component] = my_file_create_subgroup(COMP_PATH+"/"+component,CONFIG_FILE)

        # 基线的闭源库    
        print('    -> libs')
        json_root['libs'] = my_file_create_subgroup(LIBS_PATH)

        # 基线的头文件
        print('    -> include')
        json_root['include'] = my_file_create_subgroup(INCLUDE_PATH)
    else:
        # 按照 depend.json 指定的基线中的开源组件进行加载
        print('    -> components')
        components_list=depend['base']['components']
        for component in components_list:
            print('        -> '+component)
            json_root['components'][component] = my_file_create_subgroup(COMP_PATH+"/"+component,CONFIG_FILE)

        # 按照 depend.json 指定的基线中的闭源组建进行加载
        print('    -> libs')
        h_list=[]
        c_list=[]
        l_list=[]
        libs_list=depend['base']['libs']
        for lib in libs_list:
            print('        -> '+lib)
            lib_name = lib.split(".")[0]
            if lib_name.startswith('lib'):
                lib_name = lib_name[3:]
            
            lib_path = "$PROJECT_ROOT/libs/"+lib
            lib_head_file_path = "$PROJECT_ROOT/include/components/"+lib_name+"/include"
            l_list.append(lib_path)
            h_list.append(lib_head_file_path)
            
        json_root['libs'] = {'c_files':list(set(c_list)),'h_dir':list(set(h_list)),'l_files':list(set(l_list))}
        json_root['include']['vendor'] = my_file_create_subgroup(INCLUDE_PATH+'/vendor')
        json_root['include']['base'] = my_file_create_subgroup(INCLUDE_PATH+'/base')
```



</br>

### 4. 要求

无

