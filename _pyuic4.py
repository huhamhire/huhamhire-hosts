#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  _pyuic4.py : Tools update the UI code from UI design
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

GUI_DIR = './gui/'

for root, dirs, files in os.walk(GUI_DIR):
    for f in files:
        file_path = os.path.join(root, f)
        if f.endswith('.ui'):
            os.system('pyuic4 -o %s.py -x %s'
                      % (file_path.rsplit('.', 1)[0], file_path))
        elif f.endswith('.qrc'):
            os.system('pyrcc4 -o %s_rc.py %s'
                      % (os.path.join(GUI_DIR, f.rsplit('.', 1)[0]),
                         file_path))
        else:
            pass
