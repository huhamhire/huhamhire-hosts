#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# common.py : Basic utilities used by Hosts Setup Utility
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
    """Basic tools for Hosts Setup Utility

    CommonUtil class contains a set of basic tools for Hosts Setup Utility to
    use.
    """
    @classmethod
    def check_connection(cls, link):
        """ Check connect to a server - Class Method

        Check connect to a specified server by link ({link}).

        Args:
            link (str): A string indicating the link to a specified server.
                This string could be a domain name or the IP address of a
                server.

        Returns:
            A flag integer indicating whether the connection is good or not.
            1: OK, 0: Error.
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
        """Check OS - Class Method

        Check information about current operating system.

        Returns:
            (system, hostname, path, encode, flag)
            system (str): A string indicating the platform of current OS.
            hostname (str): A string indicating the hostname of current OS.
            path (str): A string indicating the path to hosts on current
                operating system.
            encode (str): A string indicating the encoding of current OS.
            flag (int): A flag integer indicating whether the current OS is
                supported or not. 1: supported, 2, unsupported.
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
        """Check user privileges - Class Method

        Check whether the current session has privileges to change the hosts
        file of current operating system.

        Returns:
            (username, flag)
            username (str): A string indicating username of the user running
                current session.
            flag (bool): A bool flag indicating whether the current session
                has write privileges to the hosts file or not.
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
        """Read network config file

        Get configurations for mirrors to connect to.

        Returns:
            A dictionary containing tag, test url, and update url of mirrors.
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
        """Transform timestamp to readable string - Class Method

        Transform unix timestamp ({timestamp}) to a data string in ISO format.

        Args:
            timestamp (int/float): A number indicating a unix timestamp.

        Returns:
            A data string in ISO format.
        """
        l_time = time.localtime(float(timestamp))
        iso_format = "%Y-%m-%d"
        date = time.strftime(iso_format, l_time)
        return date

    @classmethod
    def convert_size(cls, bufferbytes):
        """Transform file size to readable string - Class Method

        Convert byte size ({bufferbytes}) of a file into a size string.

        Args:
            bufferbytes (int): A integer indicating the size of a file counted
                by byte.

        Returns:
            A readable size string.
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
        """Cut message into lines - Class Method

        Cut english message into lines with specified length ({length}).

        Args:
            msg (str): A string indicating the message to be cut.
            cut (int): An integer indicating the length for each line.

        Returns:
            A list containing lines from the message.
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
