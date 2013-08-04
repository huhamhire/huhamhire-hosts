#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utilities.py : Basic utilities used by Hosts Setup Utility
#
# Copyleft (C) 2013 - huhamhire hosts team <develop@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING
# THE WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE.
# =====================================================================

__version__ = "0.8"
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

__all__ = ["Utilities", "LangUtilities"]

import ConfigParser
import locale
import math
import os
import sys
import socket
import time

class Utilities(object):
    """Basic tools for Hosts Setup Utility

    Utilities class contains a set of basic tools for Hosts Setup Utility to
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
            path = ''.join([os.getenv("WINDIR"),
                "\\System32\\drivers\\etc\\hosts"])
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
                has root privileges or not.
        """
        if os.name == 'nt':
            try:
                # Only windows users with admin privileges can read the
                # C:\windows\temp
                temp = os.listdir(os.sep.join([
                    os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
            except:
                return (os.environ['USERNAME'], False)
            else:
                return (os.environ['USERNAME'], True)
        else:
            if 'SUDO_USER' in os.environ and os.geteuid() == 0:
                return (os.environ['SUDO_USER'], True)
            else:
                try:
                    return (os.environ['USERNAME'], False)
                except KeyError:
                    return (os.environ['USER'], False)

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
            mirror = {}
            mirror["tag"] = sec
            mirror["test_url"] = conf.get(sec, "server")
            mirror["update"] = conf.get(sec, "update")
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
        date = time.strftime(iso_format , l_time)
        return date

    @classmethod
    def convert_size(cls, bytes):
        """Transform file size to readable string - Class Method

        Convert byte size ({bytes}) of a file into a size string.

        Args:
            bytes (int): A integer indicating the size of a file counted by
                byte.

        Returns:
            A readable size string.
        """
        if bytes == 0:
            return "0 B"
        l_unit = int(math.log(bytes, 0x400))
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        formats = ['%.2f', '%.1f', '%d']
        size = bytes / math.pow(0x400, l_unit)
        l_num = int(math.log(size, 10))
        if l_unit >= len(units):
            l_unit = len(units) - 1
        if l_num >= len(formats):
            l_num = len(formats) - 1
        return ''.join([formats[l_num], ' ', units[l_unit]]) % (size)


class LangUtilities(object):
    """language tools for Hosts Setup Utility

    LangUtilities contains a set of language tools for Hosts Setup Utility to
    use.

    Attributes:
        language (dict): A dictionary containing supported localized language
            name for a specified locale.
    """
    language = {"de_DE": u"Deutsch",
                "en_US": u"English",
                "ja_JP": u"日本語",
                "ko_KR": u"한글",
                "ru_RU": u"Русский",
                "zh_CN": u"简体中文",
                "zh_TW": u"正體中文", }

    @classmethod
    def get_locale(cls):
        """Get locale string - Class Method

        Get the default locale of current operating system.

        Returns:
            locale (str): A string indicating the locale of current operating
                system. If the locale is not in cls.dictionary dictionary, it
                will return "en_US" as default.
        """
        lc = locale.getdefaultlocale()[0]
        if lc == None:
            lc = "en_US"
        return lc

    @classmethod
    def get_language_by_locale(cls, l_locale):
        """Get language name by locale - Class Method

        Return the name of a specified language by a locale string
        ({l_locale}).

        Args:
            l_locale (str): A string indicating a specified locale.

        Returns:
            A string indicating the localized name of a language.
        """
        try:
            return cls.language[l_locale]
        except KeyError:
            return cls.language["en_US"]

    @classmethod
    def get_locale_by_language(cls, l_lang):
        """Get locale string by language name - Class Method

        Return the locale string connecting with a specified language
        ({l_lang}).

        Args:
            l_lang (str): A string indicating the localized name of a
                language.

        Returns:
            A string indicating a specified locale.
        """
        for locl, lang in cls.language.items():
            if l_lang == lang:
                return locl
        return "en_US"
