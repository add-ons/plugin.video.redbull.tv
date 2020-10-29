# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Integration tests for Routing functionality"""

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

routing = addon.routing
now = datetime.now(dateutil.tz.tzlocal())
lastweek = now + timedelta(days=-7)


class TestRouting(unittest.TestCase):
    """TestCase class"""

    def test_main_menu(self):
        """Main menu: /"""
        addon.run(['plugin://plugin.video.redbulltv/', '0', ''])
        self.assertEqual(routing.url_for(addon.index), 'plugin://plugin.video.redbulltv/')

    def test_iptv_play(self):
        """IPTV Play: /iptv/play"""
        addon.run(['plugin://plugin.video.redbulltv/iptv/play', '0', ''])
        self.assertEqual(routing.url_for(addon.iptv_play), 'plugin://plugin.video.redbulltv/iptv/play')

    def test_discover(self):
        """Discover menu: /product/discover"""
        addon.run(['plugin://plugin.video.redbulltv/product/discover', '0', ''])
        self.assertEqual(routing.url_for(addon.browse_product, 'discover'), 'plugin://plugin.video.redbulltv/product/discover')

    def test_channels(self):
        """Channels menu: /collection/playlists::d554f1ca-5a8a-4d5c-a562-419185d57979"""
        addon.run(['plugin://plugin.video.redbulltv/collection/playlists::d554f1ca-5a8a-4d5c-a562-419185d57979', '0', ''])
        self.assertEqual(routing.url_for(addon.browse_collection, 'playlists::d554f1ca-5a8a-4d5c-a562-419185d57979'), 'plugin://plugin.video.redbulltv/collection/playlists::d554f1ca-5a8a-4d5c-a562-419185d57979')

    def test_events(self):
        """Events menu: /product/events"""
        addon.run(['plugin://plugin.video.redbulltv/product/events', '0', ''])
        self.assertEqual(routing.url_for(addon.browse_product, 'events'), 'plugin://plugin.video.redbulltv/product/events')

    def test_search(self):
        """Search menu: /product/search"""
        addon.run(['plugin://plugin.video.redbulltv/search', '0', ''])
        self.assertEqual(routing.url_for(addon.search), 'plugin://plugin.video.redbulltv/search')

    def test_collection(self):
        """Collection lookup: /collection/rrn:content:collections:6270a470-02f2-4276-a9f1-8f0d93e6a055:international"""
        addon.run(['plugin://plugin.video.redbulltv/collection/rrn:content:collections:6270a470-02f2-4276-a9f1-8f0d93e6a055:international', '0', ''])
        self.assertEqual(routing.url_for(addon.browse_collection, 'rrn:content:collections:6270a470-02f2-4276-a9f1-8f0d93e6a055:international'), 'plugin://plugin.video.redbulltv/collection/rrn:content:collections:6270a470-02f2-4276-a9f1-8f0d93e6a055:international')


if __name__ == '__main__':
    unittest.main()
