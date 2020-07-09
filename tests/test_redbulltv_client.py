#!/usr/bin/env python
import resources.lib.redbulltv_client as redbulltv
import sys
import os
import time
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class ITTestRedbulltvClient(unittest.TestCase):
    redbulltv_client = redbulltv.RedbullTVClient('4')

    def test_get_discover_categories(self):
        """
        List the categorires from the Discover Page
        Check for more than 5 categories and explicitly check the first 2
        """
        test_data = 'https://api.redbull.tv/v3/products/discover'

        result = self.redbulltv_client.get_items(test_data)

        self.assertGreater(len(result), 5)
        self.assertEqual(result[0].get("title"), "Featured")

        # # TODO Order changed, Rather loop through an make sure Featured & Daily Highlights are in the list
        # self.assertEqual(result[1].get("category"), "Daily Highlights")

    def test_get_category_items(self):
        """
        List the items for a specific category on the Discover Page
        Check for more than 5 items in the 'Featured' & 'Daily Highlights' categories
        """
        test_data = [
            ('https://api.redbull.tv/v3//collections/playlists::8492e568-626a-48a3-b0d7-6d11e0f00dc3'),
            ('https://api.redbull.tv/v3//collections/playlists::3f81040a-2f31-4832-8e2e-545b1d39d173'),
        ]

        for inp in test_data:
            result = self.redbulltv_client.get_items(inp)
            self.assertGreater(len(result), 5)

    def test_watch_now_stream(self):
        """
        Test the Watch Now Live Stream and confirm a resolution specific playlist is returned
        """
        test_data = (
            ('https://dms.redbull.tv/v3/linear-borb/_v3/playlist.m3u8'),
            [
                'https://dms.redbull.tv/v3/linear-borb/_v3/playlist.m3u8'
            ]
        )
        inp, expected = test_data
        result = self.redbulltv_client.get_stream_url(inp)
        self.assertNotEqual(result, expected[0])

    def test_search(self):
        """
        Test the Search functionality
        """
        test_data = ('https://api.redbull.tv/v3/search?q=drop')
        result = self.redbulltv_client.get_items(test_data)
        self.assertGreater(len(result), 0)

    def test_upcoming_live_event(self):
        """
        Test upcoming live events
        """
        result = self.redbulltv_client.get_items(
            "https://api.redbull.tv/v3/products/calendar")

        # Choose 'Upcoming Live Events' and pick the first from the list
        result = self.redbulltv_client.get_items(
            [item for item in result if item["title"] == "Upcoming Live Events"][0]["url"])
        result = self.redbulltv_client.get_items(result[0]["url"])

        # Choose Schedule
        result = self.redbulltv_client.get_items(
            [item for item in result if item["title"] == "Schedule"][0]["url"])

        # Find the first entry with an Upcoming Date
        result = [item for item in result if 'event_date' in item][0]
        self.assertIn('event_date', result)
        self.assertGreater(result["event_date"], time.time())


if __name__ == '__main__':
    unittest.main()
