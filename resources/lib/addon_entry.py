# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Addon entry point"""

from __future__ import absolute_import, division, unicode_literals

from xbmcaddon import Addon

import kodilogging
import kodiutils

# Reinitialise ADDON every invocation to fix an issue that settings are not fresh.
kodiutils.ADDON = Addon()
kodilogging.ADDON = Addon()

if __name__ == '__main__':
    from sys import argv
    from addon import run

    run(argv)
