#!/usr/bin/env python
# coding=utf-8
import re


# 将字符串按照字典替换
def my_string_replace_with_dict(str,dict):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], str)