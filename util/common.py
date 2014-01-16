#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# common.py : Basic utilities used by Hosts Setup Utility.
#
# Copyleft (C) 2013 - huhamhire hosts team <hosts@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING
# THE WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import ConfigParser
import math
import os
import sys
import socket
import time


class CommonUtil(object):
    """
    CommonUtil class contains a set of basic tools for Hosts Setup Utility to
    use.

    .. note:: All methods from this class are declared as `classmethod`.
    """
    @classmethod
    def check_connection(cls, link):
        """
        Check connect to a specified server by :attr:`link`.

        .. note:: This is a `classmethod`.

        :param link: The link to a specified server. This string could be a
            domain name or the IP address of a server.
        :type link: str
        :return: A flag indicating whether the connection status is good or
            not.

                ====  ======
                flag  Status
                ====  ======
                1     OK
                0     Error
                ====  ======
        :rtype: int
        """
        try:
            timeout = 3
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((link, 80))
            sock.close()
            return 1
        except:
            return 0

    @classmethod
    def check_platform(cls):
        """
        Check information about current operating system.

        .. note:: This is a `classmethod`.

        :return: system, hostname, path, encode, flag

            * system(`str`): Operating system of current session.
            * hostname(`str`): Hostname of current machine.
            * path(`str`): Path to hosts on current operating system.
            * encode(`str`): Default encoding of current OS.
            * flag(`int`): A flag indicating whether the current OS is
                supported or not.

                ====  ===========
                flag  Status
                ====  ===========
                1     supported
                2     unsupported
                ====  ===========

        :rtype: str, str, str, str, int
        """
        hostname = socket.gethostname()
        if os.name == "nt":
            system = "Windows"
            path = os.getenv("WINDIR") + "\\System32\\drivers\\etc\\hosts"
            encode = "win_ansi"
        elif os.name == "posix":
            path = "/etc/hosts"
            encode = "unix_utf8"
            if sys.platform == "darwin":
                system = "OS X"
                # Remove the ".local" suffix
                hostname = hostname[0:-6]
            else:
                system = ["Unix", "Linux"][sys.platform.startswith('linux')]
        else:
            return "Unknown", '', '', 0
        return system, hostname, path, encode, 1

    @classmethod
    def check_privileges(cls):
        """
        Check whether the current session has privileges to change the hosts
        file of current operating system.

        .. note:: This is a `classmethod`.

        :return: username, flag

            * username(`str`): Username of the user running current session.
            * flag(`bool`): A flag indicating whether the current session has
              write privileges to the hosts file or not.
        :rtype: str, bool
        """
        if os.name == 'nt':
            try:
                # Only windows users with admin privileges can read the
                # C:\windows\temp
                os.listdir(os.sep.join([
                    os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
            except:
                return os.environ['USERNAME'], False
            else:
                return os.environ['USERNAME'], True
        else:
            # Check wirte privileges to the hosts file for current user
            w_flag = os.access("/etc/hosts", os.W_OK)
            try:
                return os.environ['USERNAME'], w_flag
            except KeyError:
                return os.environ['USER'], w_flag

    @classmethod
    def set_network(cls, conf_file="network.conf"):
        """
        Get configurations for mirrors to connect to.

        .. note:: This is a `classmethod`.

        :param conf_file: Path to a configuration file containing which
            contains the server list.
        :type conf_file: str
        :return: `tag`, `test url`, and `update url` of the servers listed in
            the configuration file.

            Definition of the dictionary returned:

                ========  ===================================================
                Key       Value
                ========  ===================================================
                tag       `Tag` string of a specified server.
                label     Name of a specified server.
                test_url  `URL` to test the connection to a server.
                update    `URL` containing the directory to get latest hosts\
                          data file.
                ========  ===================================================

        :rtype: dict
        """
        conf = ConfigParser.ConfigParser()
        conf.read(conf_file)
        mirrors = []
        for sec in conf.sections():
            mirror = {"tag": sec,
                      "label": conf.get(sec, "label"),
                      "test_url": conf.get(sec, "server"),
                      "update": conf.get(sec, "update"), }
            mirrors.append(mirror)
        return mirrors

    @classmethod
    def timestamp_to_date(cls, timestamp):
        """
        Transform unix :attr:`timestamp` to a data string in ISO format.

        .. note:: This is a `classmethod`.

        :param timestamp: A unix timestamp indicating a specified time.
        :type timestamp: number

            .. note:: The :attr:`timestamp` could be `int` or `float`.

        :return: Date in ISO format, which is `YY-mm-dd` in specific.
        :rtype: str
        """
        l_time = time.localtime(float(timestamp))
        iso_format = "%Y-%m-%d"
        date = time.strftime(iso_format, l_time)
        return date

    @classmethod
    def convert_size(cls, bufferbytes):
        """
        Convert byte size :attr:`bufferbytes` of a file into a size string.

        .. note:: This is a `classmethod`.

        :param bufferbytes: The size of a file counted in bytes.
        :type bufferbytes: int
        :return: A readable size string.
        :rtype: str
        """
        if bufferbytes == 0:
            return "0 B"
        l_unit = int(math.log(bufferbytes, 0x400))
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        formats = ['%.2f', '%.1f', '%d']
        size = bufferbytes / math.pow(0x400, l_unit)
        l_num = int(math.log(size, 10))
        if l_unit >= len(units):
            l_unit = len(units) - 1
        if l_num >= len(formats):
            l_num = len(formats) - 1
        return ''.join([formats[l_num], ' ', units[l_unit]]) % size

    @classmethod
    def cut_message(cls, msg, cut):
        """
        Cut english message (:attr:`msg`) into lines with specified length
        (:attr:`cut`).

        .. note:: This is a `classmethod`.

        :param msg: The message to be cut.
        :type msg: str
        :param cut: The length for each line of the message.
        :type cut: int
        :return: Lines cut from the message.
        :rtype: list
        """
        delimiter = [" ", "\n"]
        msgs = []
        while len(msg) >= cut:
            if "\n" in msg[:cut-1]:
                [line, msg] = msg.split("\n", 1)
            else:
                if (msg[cut-1] not in delimiter) and \
                        (msg[cut] not in delimiter):
                    cut_len = cut - 1
                    hyphen = " " if msg[cut-2] in delimiter else "-"
                else:
                    cut_len = cut
                    hyphen = " "
                line = msg[:cut_len] + hyphen
                msg = msg[cut_len:]
            msgs.append(line)
        msgs.append(msg)
        return msgs
