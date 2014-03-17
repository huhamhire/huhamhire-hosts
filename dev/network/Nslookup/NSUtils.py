#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import re
import struct


class NSUtils(object):

    @staticmethod
    def encode(host_name):
        index = os.urandom(2)
        host_str = ''.join(chr(len(x)) + x for x in host_name.split('.'))
        data = "%s\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00%s" \
               "\x00\x00\x01\x00\x01" % (index, host_str)
        data = struct.pack("!H", len(data)) + data
        return data

    @staticmethod
    def decode(in_sock):
        in_file = in_sock.makefile("rb")
        size = struct.unpack("!H", in_file.read(2))[0]
        data = in_file.read(size)
        ip_list = re.findall("\xC0.\x00\x01\x00\x01.{6}(.{4})", data)
        return [".".join(str(ord(x)) for x in s) for s in ip_list]