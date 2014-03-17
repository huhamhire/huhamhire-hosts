#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py : Declare modules to be called in network module.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

from nslookup import MultiNSLookup
from HttpTest import MultiHttpTest
from PingTest import MultiPingTest

__all__ = ["MultiNSLookup", "MultiHttpTest", "MultiPingTest"]