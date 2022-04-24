#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

setup(name='all_in_one_ide_tool',
     version='0.1',
     description='TuyaOS All in One IDE Tool',
     url='https://github.com/nbtool/all_in_one_ide_tool',
     author='beautifulzzzz',
     author_email='beautifulzzzz@qq.com',
     license='MIT',
     packages=['./'],
    install_requires=[
        'GitPython >= 3.1.27',
        'lxml >= 4.8.0'
    ],
    zip_safe=False)
