#!/bin/bash
# bash gitx.sh s [a/c/v]
# bash gitx.sh d [a/c/v]

num=$#
cmd=$1

declare -A dic
dic=([a]="apps" [c]="components" [ac]="application_components" [v]="vendor" [ad]="adapter")

function GIT_STATUS(){
    echo $1+"------------------------"
    dir_root=$1
        
    if [ ! -d $dir_root ]; then
        echo "no dir!"
    fi
        
    sub_dir=`ls $dir_root`
    for dir in $sub_dir
    do
        echo "> "$dir
        cd $dir_root/$dir
       
        if [ ! -d ".git" ]; then
            echo "  - no git!"
        else
	        git config core.filemode false
            git status -s
        fi

        cd - > /dev/null
    done
    echo ""
}

function GIT_DIFF(){
    echo $2+"------------------------"
    dir_root=$2
        
    if [ ! -d $dir_root ]; then
        echo "no dir!"
    fi
    
    if [ "$1" == "dirs" ];then
        sub_dir=`ls $dir_root`
    else
        sub_dir="."
    fi
    
    for dir in $sub_dir
    do
        echo "> "$dir
        cd $dir_root/$dir

        if [ ! -d ".git" ]; then
            echo "  - no git!"
        else
            git diff
        fi

        cd - > /dev/null
    done
    echo ""
}

####################################################

if [ "$cmd" == "s" ];then
    if [ $num == 1 ];then
        GIT_STATUS application_components
        GIT_STATUS components
        GIT_STATUS adapter
        GIT_STATUS vendor
        GIT_STATUS apps
    fi
    if [ $num == 2 ];then
        sub_dir=${dic[$2]}
        GIT_STATUS $sub_dir
    fi
elif [ "$cmd" == "d" ];then
    if [ $num == 1 ];then
        GIT_DIFF application_components
        GIT_DIFF "dirs" components
	    GIT_DIFF "dirs" adapter
        GIT_DIFF "dirs" vendor
        GIT_DIFF "dirs" apps
    fi
    if [ $num == 2 ];then
        sub_dir=${dic[$2]}
        GIT_DIFF "dirs" $sub_dir
    fi
    if [ $num == 3 ];then
        sub_dir=${dic[$2]}/$3
        GIT_DIFF "dir" $sub_dir
    fi
else
    echo "Usage: bash gitx.sh cmd [sub_dir] [git_repository_name]"
    echo "cmd options:"
    echo " -> s: git satus"
    echo " -> d: git diff"
    echo " "
     
    echo "sub_dir options:"   
    echo " -> a: app sub_dir"
    echo " -> c: components sub_dir"
    echo " -> ac: application_components sub_dir"
    echo " -> ad: adapter"
    echo " -> v: vendor sub_dir"
    echo " "

    echo "git_repository_name:"
    echo " -> the name of one repository in the sub_dir"
    echo " "
    echo "-----"
    echo "bash gitx.sh s c #for list the status of all the git repository in components"
fi
