# -*- coding: UTF-8 -*-
# by huhamhire
import py_compile
import os

file_name = 'hosts_setup_OnL.py'
path = os.path.dirname(__file__)
file = path[0:-7] + file_name
py_compile.compile(file)