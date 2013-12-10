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

import locale


class LangUtil(object):
    """language tools for Hosts Setup Utility

    LangUtil contains a set of language tools for Hosts Setup Utility to
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
        if lc is None:
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
