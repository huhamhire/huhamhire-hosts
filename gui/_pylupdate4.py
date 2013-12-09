#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _pylupdate4.py : Tools to update the language files for UI
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

import os

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pro'):
            os.system('pylupdate4 %s' % file)
