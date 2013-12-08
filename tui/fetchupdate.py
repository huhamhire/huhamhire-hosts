#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fetchupdate.py:
#
# Copyleft (C) 2013 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

__all__ = [ 'FetchUpdate' ]

import os
import socket
import urllib

class FetchUpdate(object):
    def __init__(self, parent):
        mirror_id = parent.settings[0][1]
        mirror = parent.settings[0][2][mirror_id]
        self.url = mirror["update"] + parent.filename
        self.path = "./" + parent.filename
        self.tmp_path = self.path + ".download"
        self.filesize = parent.update["size"]
        self.parent = parent

    def get_file(self):
        socket.setdefaulttimeout(10)
        try:
            urllib.urlretrieve(self.url, self.tmp_path,
                self.parent.process_bar)
            self.replace_old()
        except Exception, e:
            raise e

    def replace_old(self):
        """Replace the old data file - Public Method

        Overwrite the old hosts data file with the new one.
        """
        if os.path.isfile(self.path):
            os.remove(self.path)
        os.rename(self.tmp_path, self.path)