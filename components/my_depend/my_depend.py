#!/usr/bin/env python3
# coding=utf-8
import os
import sys
import pip

class my_depend():
    def __init__(self):
        return

    def check(self):
        _IS_WINDOWS = os.name == "nt"  # Are we running on Windows?

        try:
            from git import Repo
        except:
            self.__check_and_install('git','GitPython')

        try:
            from kconfiglib import Symbol
        except:
            self.__check_and_install('kconfiglib','kconfiglib')           

        try:
            import lxml
        except ImportError as e:
            self.__check_and_install('lxml','lxml')
            
        try:
            import curses
        except ImportError as e:
            if _IS_WINDOWS:
                self.__check_and_install('windows-curses','windows-curses')              

    def __check_and_install(self,KEY,MODULE):
        if not KEY in sys.modules.keys():
            print('install',MODULE)
            pip.main(['install', MODULE])
