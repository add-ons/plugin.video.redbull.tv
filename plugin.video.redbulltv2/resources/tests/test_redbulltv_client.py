#!/usr/bin/env python
import sys, os, time
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib.redbulltv_client as redbulltv

class ITTestRedbulltvClient(unittest.TestCase):
    redbulltv_client = redbulltv.RedbullTVClient('4')

    def test_get_root_menu(self):
        test_data = [
            (
                None,
                [
                    {'url': 'https://appletv-v2.redbull.tv/views/discover', 'is_content': False, 'title': 'Discover'},
                    {'url': 'https://appletv-v2.redbull.tv/views/tv', 'is_content': False, 'title': 'TV'},
                    {'url': 'https://appletv-v2.redbull.tv/views/channels', 'is_content': False, 'title': 'Channels'},
                    {'url': 'https://appletv-v2.redbull.tv/views/calendar', 'is_content': False, 'title': 'Calendar'},
                    {'url': 'https://appletv-v2.redbull.tv/search?q=', 'is_content': False, 'title': 'Search'}
                ]
            ),
        ]
        for inp, expected in test_data:
            self.assertEqual(self.redbulltv_client.get_items(inp), expected)

    def test_get_discover_categories(self):
        """
        List the categorires from the Discover Page
        Check for more than 5 categories and explicitly check the first 2
        """
        test_data = ('https://appletv-v2.redbull.tv/views/discover', None)

        result = self.redbulltv_client.get_items(*test_data)
        self.assertGreater(len(result), 5)
        self.assertEqual(result[0].get("category"), "Featured")
        self.assertEqual(result[1].get("category"), "Daily Highlights")

    def test_get_category_items(self):
        """
        List the items for a specific category on the Discover Page
        Check for more than 5 items in the 'Featured' & 'Daily Highlights' categories
        """
        test_data = [
            ('https://appletv-v2.redbull.tv/views/discover', 'Featured'),
            ('https://appletv-v2.redbull.tv/views/discover', 'Daily Highlights'),
        ]

        for inp in test_data:
            result = self.redbulltv_client.get_items(*inp)
            self.assertGreater(len(result), 5)

    def test_watch_now_stream(self):
        """
        Test the Watch Now Live Stream and confirm a resolution specific playlist is returned
        """
        test_data = (
            ('https://appletv-v2.redbull.tv/linear_stream', None),
            [
                ('Lean back and experience the best of Red Bull TV', True, 'Watch Now'),
                'https://dms.redbull.tv/v3/linear-borb/_v3/playlist.m3u8'
            ]
        )
        inp, expected = test_data
        result = self.redbulltv_client.get_items(*inp)
        self.assertEqual(
            (result[0].get("summary"), result[0].get("is_stream"), result[0].get("title")),
            expected[0]
        )
        self.assertNotEqual(result[0].get('url'), expected[1])

    def test_search(self):
        """
        Test the Search functionality
        """
        test_data = ('https://appletv-v2.redbull.tv/search?q=follow', None)
        result = self.redbulltv_client.get_items(*test_data)
        self.assertGreater(len(result), 0)

    def test_upcoming_live_event(self):
        """
        Test upcoming live events
        """
        result = self.redbulltv_client.get_items("https://appletv-v2.redbull.tv/views/calendar", "Upcoming Live Events")
        result = self.redbulltv_client.get_items(result[0]["url"])
        result = self.redbulltv_client.get_items([item for item in result if item["title"] == "Schedule"][0]["url"])
        self.assertIn('event_date', result[0])
        self.assertGreater(result[0]["event_date"], time.time())

if __name__ == '__main__':
    unittest.main()
