# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Integration tests for IPTV Manager functionality"""

# pylint: disable=invalid-name,line-too-long

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime, timedelta
import unittest
import dateutil.tz
import addon

xbmc = __import__('xbmc')
xbmcaddon = __import__('xbmcaddon')
xbmcgui = __import__('xbmcgui')
xbmcplugin = __import__('xbmcplugin')
xbmcvfs = __import__('xbmcvfs')

plugin = addon.plugin
now = datetime.now(dateutil.tz.tzlocal())
lastweek = now + timedelta(days=-7)


class TestIPTVManager(unittest.TestCase):
    """TestCase class"""

    def test_get_iptv_channels(self):
        """Get IPTV channels"""
        from redbull import RedBullTV
        iptv_channels = RedBullTV().get_iptv_channels()
        # print(iptv_channels)
        self.assertTrue(iptv_channels)

    def test_get_iptv_epg(self):
        """Get IPTV EPG"""
        from redbull import RedBullTV
        iptv_epg = RedBullTV().get_iptv_epg()
        # print(iptv_epg)
        self.assertTrue(iptv_epg)


if __name__ == '__main__':
    unittest.main()
