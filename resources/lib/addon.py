# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
""" Addon code """

from __future__ import absolute_import, division, unicode_literals

import json
import logging
import time
import urllib
import urllib2
from routing import Plugin

import xbmc
import xbmcgui
import xbmcplugin

import kodilogging
from kodiutils import addon_icon, addon_id, get_search_string, localize, play

kodilogging.config()
routing = Plugin()  # pylint: disable=invalid-name
_LOGGER = logging.getLogger('addon')
REDBULL_STREAMS = "https://dms.redbull.tv/v3/"
REDBULL_API = "https://api.redbull.tv/v3/"
COLLECTION = 1
PRODUCT = 2


@routing.route('/')
def show_main_menu():
    """ Show the main menu """
    RedBullTV().navigation()


@routing.route('/iptv/play')
def iptv_play():
    RedBullTV().play_live()


@routing.route('/iptv/channels')
def iptv_channels():
    """ Generate channel data for the Kodi PVR integration """
    from iptvmanager import IPTVManager
    IPTVManager(int(routing.args['port'][0])).send_channels()  # pylint: disable=too-many-function-args


@routing.route('/iptv/epg')
def iptv_epg():
    """ Generate EPG data for the Kodi PVR integration """
    from iptvmanager import IPTVManager
    IPTVManager(int(routing.args['port'][0])).send_epg()  # pylint: disable=too-many-function-args


def run(params):
    """ Run the routing plugin """
    routing.run(params)


def get_json(url, token=None):
    try:
        request = urllib2.Request(url)
        if token:
            request.add_header("Authorization", token)
        response = urllib2.urlopen(request)
    except urllib2.URLError as err:
        raise IOError(*err.reason)
    else:
        return json.loads(response.read())


class RedBullTV:

    def __init__(self):
        self.base_url = 'plugin://' + addon_id() + routing.path
        self.addon_handle = routing.handle
        self.args = routing.args
        xbmcplugin.setContent(self.addon_handle, 'videos')
        self.default_view_mode = 55  # Wide List
        self.token = get_json(REDBULL_API + "session?category=smart_tv&os_family=android")["token"]

    def get_epg(self):
        return get_json(REDBULL_API + "epg?complete=true", self.token)

    def play_live(self):
        self.play_stream(REDBULL_STREAMS + "linear-borb/" + self.token + "/playlist.m3u8")

    def navigation(self):
        url = self.args.get("api_url")[0].decode('base64') if self.args.get("api_url") else None

        # If Stream url is available
        if self.args.get('is_stream', [False])[0] == "True":
            self.play_stream(url)
            return

        if url and "search?q=" in url:
            url += get_search_string()

        try:
            items = self.get_items(url)
        except IOError:
            # Error getting data from Redbull server
            xbmcgui.Dialog().ok(localize(30020), localize(30021), localize(30022))
            return

        if not items:
            # No results found
            xbmcgui.Dialog().ok(localize(30023), localize(30024), localize(30025))
            return

        if items[0].get("event_date"):
            # Scheduled Event Time
            xbmcgui.Dialog().ok(localize(30026), localize(30027), items[0].get('event_date') + ' (GMT+' + str(time.timezone / 3600 * -1) + ')')
            return

        self.add_items(items)

        xbmc.executebuiltin('Container.SetViewMode(%d)' % self.default_view_mode)
        xbmcplugin.endOfDirectory(self.addon_handle)

    def add_items(self, items):
        for item in items:
            params = dict(
                api_url=item["url"].encode('base64'),
            )

            list_item = xbmcgui.ListItem(item.get("title"))
            list_item.setArt({"thumb": item['landscape'] if 'landscape' in item else addon_icon()})

            if item.get("is_content"):
                params['is_stream'] = item["is_content"]
                list_item.setProperty('IsPlayable', 'true')
            if 'fanart' in item:
                list_item.setArt({"fanart": item['fanart']})
            if 'landscape' in item:
                list_item.setArt({"landscape": item['landscape']})
            if 'banner' in item:
                list_item.setArt({"banner": item['banner']})
            if 'poster' in item:
                list_item.setArt({"poster": item['poster']})

            info_labels = {
                "title": item["title"],
                "plot": item.get("summary", None),
                "genre": item.get("subheading", None),
                "duration": item.get("duration")
            }
            list_item.setInfo(type="Video", infoLabels=info_labels)
            nav_url = self.base_url + '?' + urllib.urlencode(params)
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=nav_url, listitem=list_item, isFolder=(not item["is_content"]))

    @staticmethod
    def play_stream(master_m3u8_url):
        play(master_m3u8_url)

    @staticmethod
    def get_image_url(element_id, resources, element_type, width=1024, quality=70):
        url = "https://resources.redbull.tv/" + element_id + "/"

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

    def get_element_details(self, element, element_type):
        details = {"is_content": False}
        if element.get("playable") or element.get("action") == "play":
            details["is_content"] = True
            details["url"] = REDBULL_STREAMS + \
                element["id"] + "/" + self.token + "/playlist.m3u8"
            if element.get("duration"):
                details["duration"] = element.get("duration") / 1000
        # Handle video types that are actually upcoming events
        elif 'type' in element and element.get('type') == "video" and 'status' in element and element.get("status").get("label") == "Upcoming":
            details["event_date"] = element.get("status").get("start_time")
        elif element_type == COLLECTION:
            details["url"] = REDBULL_API + \
                "collections/" + element["id"]  # + "?limit=20"
        elif element_type == PRODUCT:
            details["url"] = REDBULL_API + \
                "products/" + element["id"]  # +"?limit=20"

        details["title"] = (element.get("label") or element.get("title"))
        details["subheading"] = element.get("subheading")
        details["summary"] = element.get("long_description") if element.get("long_description") else element.get("short_description")
        if element.get("resources"):
            details["landscape"] = self.get_image_url(element.get("id"), element.get("resources"), "landscape")
            details["fanart"] = self.get_image_url(element.get("id"), element.get("resources"), "landscape")
            details["banner"] = self.get_image_url(element.get("id"), element.get("resources"), "banner")
            details["thumb"] = self.get_image_url(element.get("id"), element.get("resources"), "thumb")
            details["poster"] = self.get_image_url(element.get("id"), element.get("resources"), "poster")

        # Strip out any keys with empty values
        return {k: v for k, v in details.items() if v is not None}

    def get_items(self, url=None, page=1, limit=20):

        items = []

        # If no url is specified, return the root menu
        if url is None:
            return [
                {"title": "Live TV", "url": REDBULL_STREAMS + "linear-borb/" + self.token + "/playlist.m3u8", "is_content": True},
                {"title": "Discover", "url": REDBULL_API + "products/discover", "is_content": False},
                {"title": "Browse", "url": REDBULL_API + "products/channels", "is_content": False},
                {"title": "Events", "url": REDBULL_API + "products/events", "is_content": False},
                {"title": "Search", "url": REDBULL_API + "search?q=", "is_content": False},
            ]

        result = get_json(url + ('?', '&')['?' in url] + 'limit=' + str(limit) + '&offset=' + str((page - 1) * limit), self.token)

        if 'links' in result:
            links = result["links"]
            for link in links:
                items.append(self.get_element_details(
                    link, PRODUCT))

        if 'collections' in result:
            collections = result["collections"]

            # Handle Search results
            if collections and collections[0].get("collection_type") == "top_results":
                result["items"] = collections[0]["items"]
            else:
                for collection in collections:
                    items.append(self.get_element_details(
                        collection, COLLECTION))

        if 'items' in result:
            result_items = result["items"]
            for result_item in result_items:
                items.append(self.get_element_details(
                    result_item, PRODUCT))

        return items
