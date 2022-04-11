# 当前 makefile 文件所在目录
define my-dir
$(strip	\
	$(eval _md_file_:=$$(lastword $$(MAKEFILE_LIST)))	\
	$(if $(filter $(CLEAR_VARS),$(_md_file_)),	\
		$(error LOCAL_PATH must be set before including $$(CLEAR_VARS))	\
		,	\
		$(patsubst %/,%,$(dir $(_md_file_)))	\
	)	\
)
endef

include $(CONFIG)
ifneq ($(wildcard $(LOCAL_PATH)/local.mk),)
include $(LOCAL_PATH)/local.mk
endif



# Makefile中使用定义空格变量，并对其查找替换
# https://blog.csdn.net/zxygww/article/details/49278479
# Makefile常用字符串处理函数
# http://c.biancheng.net/view/7093.html
NULLSTRING:=
SPACE:=$(NULLSTRING) #end
TARGET:=\",\"
C_FILES=$(subst $(SPACE),$(TARGET),$(strip $(LOCAL_SRC_FILES)))
H_DIRS=$(subst $(SPACE),$(TARGET),$(strip $(TUYA_SDK_INC)))

kconfig:
	@echo "{\"c_files\":[\"$(C_FILES)\"],\"h_dir\":[\"$(H_DIRS)\"]}" > $(LOCAL_PATH)/subdir.json
	

