#!/bin/sh

# CI系统传入的参数说明：
#
# $1 - 产品目录，如： apps/product1
# $2 - 产品名称，如： product1
# $3 - 产品版本，如： 1.0.0
# $4 - 产物包路径，如： output/dist/product1_1.0.0
# $5 - 固件标识符


cd `dirname $0`

# 通过环境变量传递生成的产物包全路径名称
export CI_PACKAGE_PATH="$(pwd)/$4"
export CI_IDENTIFIER=$5

APP_PATH=$1
FW_VERSION=`echo $3 | sed "s:\(.*\)-beta.*:\1:g"`  # 去掉 bate

OUTPUT=$4
OUTPUT_PATH=$(dirname $OUTPUT)
OUTPUT_NAME=$(basename $OUTPUT)

echo -e "Build APP SDK Begin"

echo $OUTPUT_PATH
echo $OUTPUT_NAME

./prepare.sh $2 || exit 11
python build_app.py "$1" "$5" $FW_VERSION 'build' $OUTPUT_PATH || exit 12
python build_app.py "$1" "$5" $FW_VERSION 'sdk' $OUTPUT_PATH || exit 12


# 打包
cd $OUTPUT_PATH
tar -zcf $OUTPUT_NAME $2
rm -rf $2


echo -e "Build Finish"
