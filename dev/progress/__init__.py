#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py : Declare modules to be called in progress module.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

from LoggerView import LoggerView
from ProgressWidget import ProgressWidget

__all__ = ["LoggerView", "ProgressWidget"]