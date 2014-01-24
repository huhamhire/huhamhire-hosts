#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  language.py : Language utilities used in GUI module.
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
    """
    LangUtil contains a set of language tools for Hosts Setup Utility to
    use.

    .. note:: All methods from this class are declared as `classmethod`.

    :ivar dict language: Supported localized language name for a specified
        locale tag.

        The default declaration of :attr:`language` is::

            language = {"de_DE": u"Deutsch",
                        "en_US": u"English",
                        "ja_JP": u"日本語",
                        "ko_KR": u"한글",
                        "ru_RU": u"Русский",
                        "zh_CN": u"简体中文",
                        "zh_TW": u"正體中文", }

        .. note:: The keys of :attr:`language` are typically in the format of \
            IETF language tag. For example: en_US, en_GB, etc.

        .. note:: The Hosts Setup Utility would check whether the language
            files exist in `gui/lang/` folder automatically while loading GUI.
            If not, the language related wouldn't be available in language
            selection combobox.
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
        """
        Retrieve the default locale tag of current operating system.

        .. note:: This is a `classmethod`.

        :return: Default locale tag of current operating system. If the locale
            is not found in cls.dictionary dictionary, the return value
            "en_US" as default.
        :rtype: str
        """
        lc = locale.getdefaultlocale()[0]
        if lc is None:
            lc = "en_US"
        return lc

    @classmethod
    def get_language_by_locale(cls, l_locale):
        """
        Return the name of a specified language by :attr:`l_locale`.

        .. note:: This is a `classmethod`.

        :param l_locale: Locale tag of a specified language.
        :type l_locale: str
        :return: Localized name of a specified language.
        :type: str
        """
        try:
            return cls.language[l_locale]
        except KeyError:
            return cls.language["en_US"]

    @classmethod
    def get_locale_by_language(cls, l_lang):
        """
        Get the locale string connecting with a language specified by
        :attr:`l_lang`.

        .. note:: This is a `classmethod`.

        :param l_lang: Localized name of a specified language.
        :type l_lang: unicode
        :return: Locale tag of a specified language.
        :rtype: str
        """
        for locl, lang in cls.language.items():
            if l_lang == lang:
                return locl
        return "en_US"
