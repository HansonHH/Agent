#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""
import gzip
import zlib

str1 = open('Image.gzip', 'rb').read()
str2 = zlib.decompress(str1)

f = open('RecoveredFile', 'wb')
f.write(str2)
f.close()

#with gzip.open("Image.gzip", 'rb') as f:
#    file_content = f.read()
