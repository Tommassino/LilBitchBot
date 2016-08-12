# -*- coding: utf-8 -*-

"""
LilBitch Bot
:copyright: (c) 2016-2017 Tommassino
:license: MIT, see LICENSE for more details.
"""

__title__ = 'lilbitch'
__author__ = 'Tommassino'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016-2017 Tommassino'
__version__ = '0.1.0'

from collections import namedtuple

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=1, micro=0, releaselevel='final', serial=0)
