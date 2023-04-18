
### 1.目的

如果文件不排序，会导致同一个环境下每次由于链接 .o 文件的顺序不同，导致生成最终固件不一样，因此这里实现对文件排序。

</br>

### 2.操作

优化 `my_file_create_subgroup` 实现搜索完文件后，进行去重和排序。

```Bash
 M ../components/my_file/my_file.py
 M ../components/my_ide/my_ide_front.py
 M 03-tag_support_app_config_need_libs.md
```

</br>

### 3. 实现

#### 3.1 my_file.py

原来对于搜索完的文件，采用 set 去重：

```Python
ret = {'c_files':list(set(c_list)),'h_dir':list(set(h_list)),'l_files':list(set(l_list))}
```

set 去重最大的缺点就是会将顺序随即，也就是说每次运行，顺序都可能不一样。因此封装一个去重+排序的接口：

```Python
def __list_distinct_and_sort(mlist):
    if len(mlist) == 0:
        return mlist
    else:
        #https://www.zhihu.com/question/57741762
        return sorted(list(dict.fromkeys(mlist)))
```

#### 3.2 my_ide_front.py

仅仅将：

```Python
json_root['libs'] = {'h_dir':list(set(h_list)),'l_files':list(dict.fromkeys(l_list))}
```

改为：

```Python
json_root['libs'] = {'h_dir':list(dict.fromkeys(h_list)),'l_files':list(dict.fromkeys(l_list))}
```

注意：最终可以做到，保留 vendor.json 的默认顺序，然后每个子块内（App\每个组件\TKL等） .h\.c\lib 进行去重和排序。既能保持底层的顺序正常，又能保证在不同电脑上编译不会由于顺序随即而产生不同固件不。

</br>

### 4. 要求

无

