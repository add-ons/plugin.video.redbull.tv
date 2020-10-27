# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
""" Implementation of RedBullTV class """

from __future__ import absolute_import, division, unicode_literals
import kodiutils
import kodilogging
import urllib2
import json
from kodiutils import addon_icon, addon_id, localize


class RedBullTV():

    REDBULL_STREAMS = "https://dms.redbull.tv/v3/"
    REDBULL_API = "https://api.redbull.tv/v3/"
    REDBULL_RESOURCES = "https://resources.redbull.tv/"


    def __init__(self):
        self.token = self.get_json(self.REDBULL_API + "session?category=smart_tv&os_family=android")["token"]


    def get_play_url(self, uid):
        return self.REDBULL_STREAMS + uid + '/' + self.token + "/playlist.m3u8"


    def get_collection_url(self, uid):
        return self.REDBULL_API +  "collections/" + uid


    def get_product_url(self, uid):
        return self.REDBULL_API +  "products/" + uid


    def get_search_url(self, query):
        return self.REDBULL_API + "search?q=" + query


    def get_json(self, url, token=None):
        try:
            request = urllib2.Request(url)
            if token:
                request.add_header("Authorization", token)
            response = urllib2.urlopen(request)
        except urllib2.URLError as err:
            raise IOError(*err.reason)
        else:
            return json.loads(response.read())          


    def get_epg(self):
        return self.get_json(self.REDBULL_API + "epg?complete=true", self.token)


    def get_image_url(self, element_id, resources, element_type, width=1024, quality=70):
        url = self.REDBULL_RESOURCES + element_id + "/"

        if element_type == "fanart" and "rbtv_background_landscape" in resources:
            url += "rbtv_background_landscape"
        if element_type == "landscape":
            if "rbtv_cover_art_landscape" in resources:
                url += "rbtv_cover_art_landscape"
            elif "rbtv_display_art_landscape" in resources:
                url += "rbtv_display_art_landscape"
            elif "rbtv_background_landscape" in resources:
                url += "rbtv_background_landscape"
            else:
                return None
        elif element_type == "banner":
            if "rbtv_cover_art_banner" in resources:
                url += "rbtv_cover_art_banner"
            elif "rbtv_display_art_banner" in resources:
                url += "rbtv_display_art_banner"
            else:
                return None
        elif element_type == "poster":
            if "rbtv_cover_art_portrait" in resources:
                url += "rbtv_cover_art_portrait"
            elif "rbtv_display_art_portrait" in resources:
                url += "rbtv_display_art_portrait"
            else:
                return None
        else:
            return None

        url += "/im"

        if width:
            url += ":i:w_1024"

        if quality:
            url += ",q_70"

        return url


    def get_content(self, url=None, page=1, limit=20):
        return self.get_json(url + ('?', '&')['?' in url] + 'limit=' + str(limit) + '&offset=' + str((page - 1) * limit), self.token)
