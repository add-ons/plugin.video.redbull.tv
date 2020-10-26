#!/usr/bin/env python
from __future__ import absolute_import, division, unicode_literals

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../resources/lib'))
from utils import strip_url, build_url


class TestUtils(unittest.TestCase):
    def test_strip_url(self):
        example_urls = [
            (
                "loadPage('https://appletv-v2.redbull.tv/linear_stream');",
                "https://appletv-v2.redbull.tv/linear_stream",
            ),
            (
                "loadPage('https://appletv-v2.redbull.tv/views/AP-1RA8Ge0f00dc3');",
                "https://appletv-v2.redbull.tv/views/AP-1RA8Ge0f00dc3",
            ),
            (
                "loadPage('https://appletv-v2.redbull.tv/content/AP-1SWSN78W');",
                "https://appletv-v2.redbull.tv/content/AP-1SWSN78W",
            ),
        ]
        for inp, expected in example_urls:
            self.assertEqual(strip_url(inp), expected)

    def test_build_url(self):
        example_urls = [
            (
                "plugin://plugin.video.redbull.tv/",
                [
                    ("function", "content"),
                    ("category", "Winning Run"),
                    ("api_url", "aHR0cHM6LyzA=\n"),
                ],
                "plugin://plugin.video.redbull.tv/?function=content&category=Winning+Run&api_url=aHR0cHM6LyzA%3D%0A",
            )
        ]
        for base_url, query, expected in example_urls:
            self.assertEqual(build_url(base_url, query), expected)


if __name__ == "__main__":
    unittest.main()
