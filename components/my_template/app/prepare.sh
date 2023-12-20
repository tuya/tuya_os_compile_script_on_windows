#!/bin/sh

print_not_null()
{
    # $1 为空，返回错误
    if [ x"$1" = x"" ]; then
        return 1
    fi

    echo "$1"
}


cd `dirname $0`

APP_NAME=`print_not_null $1 || bash ./scripts/get_app_name_cde.sh cluster.yaml ./tmp/app_names.log`
echo APP_NAME=$APP_NAME

[ -z $APP_NAME ] && echo "error: no app name!" && exit 99 


embcli update --pn $APP_NAME || exit 2

# 移动tuyaos开发框架到根目录
cp ./TuyaOS/vendor ./ -rf
cp ./TuyaOS/include ./ -rf
cp ./TuyaOS/libs ./ -rf
cp ./TuyaOS/components ./ -rf
rm ./TuyaOS -rf

