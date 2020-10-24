# -*- coding: utf-8 -*-
""" Addon code """

from __future__ import absolute_import, division, unicode_literals

import logging
import sys, time, re, os
import urlparse
import urllib, urllib2, json

import xbmcgui, xbmcplugin, xbmcaddon, xbmc
from routing import Plugin
from resources.lib import kodilogging
from resources.lib import kodiutils

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
    from resources.lib.iptvmanager import IPTVManager
    IPTVManager(int(routing.args['port'][0])).send_channels()  # pylint: disable=too-many-function-args

@routing.route('/iptv/epg')
def iptv_epg():
    """ Generate EPG data for the Kodi PVR integration """
    from resources.lib.iptvmanager import IPTVManager
    IPTVManager(int(routing.args['port'][0])).send_epg()  # pylint: disable=too-many-function-args

def run(params):
    """ Run the routing plugin """
    routing.run(params)

def build_url(base_url, query):
    return base_url + '?' + urllib.urlencode(query)

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
        self.base_url = sys.argv[0]
        self.addon_handle = int(sys.argv[1])
        self.args = urlparse.parse_qs(sys.argv[2][1:])
        xbmcplugin.setContent(self.addon_handle, 'videos')
        self.default_view_mode = 55 # Wide List
        self.token = get_json(REDBULL_API + "session?category=smart_tv&os_family=android")["token"]

    def get_epg(self):
        return get_json(REDBULL_API + "epg?complete=true", self.token)

    def play_live(self):
        item = xbmcgui.ListItem(path=REDBULL_STREAMS + "linear-borb/" + self.token + "/playlist.m3u8")
        xbmcplugin.setResolvedUrl(handle=self.addon_handle, succeeded=True, listitem=item)

    def navigation(self):
        url = self.args.get("api_url")[0].decode('base64') if self.args.get("api_url") else None
        is_stream = self.args.get('is_stream', [False])[0] == "True"

        if url and "search?q=" in url:
            url += kodiutils.get_search_string()

        # If Stream url is available
        if is_stream:
            self.play_stream(url)
            return

        try:
            items = self.get_items(url)
        except IOError:
            # Error getting data from Redbull server
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30020), self.addon.getLocalizedString(30021), self.addon.getLocalizedString(30022))
            return

        if not items:
            # No results found
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30023), self.addon.getLocalizedString(30024), self.addon.getLocalizedString(30025))
            return
        elif items[0].get("event_date"):
            # Scheduled Event Time
            xbmcgui.Dialog().ok(
                self.addon.getLocalizedString(30026),
                self.addon.getLocalizedString(30027),
                items[0].get("event_date") + " (GMT+" + str(time.timezone / 3600 * -1) + ")"
            )
            return
        else:
            self.add_items(items)

        xbmc.executebuiltin('Container.SetViewMode(%d)' % self.default_view_mode)
        xbmcplugin.endOfDirectory(self.addon_handle)

    def add_items(self, items):
        for item in items:
            params = {
                'api_url': item["url"].encode('base64'),
                }

            url = build_url(self.base_url, params)
            list_item = xbmcgui.ListItem(item.get("title"))
            list_item.setArt({"thumb": item['landscape'] if 'landscape' in item else kodiutils.getAddonInfo('icon')})

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
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=(not item["is_content"]))

    def play_stream(self, streams_url):
        stream_url = self.get_stream_url(streams_url)
        item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(handle=self.addon_handle, succeeded=True, listitem=item)

    @staticmethod
    def get_resolution_code(video_resolution_id):
        return {
            "0": "320x180",
            "1": "426x240",
            "2": "640x360",
            "3": "960x540",
            "4": "1280x720",
        }.get(video_resolution_id, "1920x1080")

    def get_stream_url(self, streams_url):
        url = streams_url
        base_url = ''

        # Try find stream for specific resolution stream, if that failed will use the
        # playlist url passed in and kodi will choose a stream
        try:
            response = urllib2.urlopen(url)
            # Required to get base url in case of a redirect, to use for relative paths
            base_url = response.geturl()
            playlists = response.read()

            resolution = self.get_resolution_code(kodiutils.getSetting('video.resolution'))
            media_url = re.search(
                "RESOLUTION=" + resolution + ".*\n(.*)",
                playlists).group(1)
        except Exception:
            pass
        else:
            url = media_url

        # if url is relative, add the base path
        if base_url != '' and not url.startswith('http'):
            url = os.path.dirname(base_url) + '/' + url

        return url

    @staticmethod
    def get_image_url(id, resources, type, width=1024, quality=70):
        url = "https://resources.redbull.tv/" + id + "/"

        if type == "fanart" and "rbtv_background_landscape" in resources:
            url += "rbtv_background_landscape"
        if type == "landscape":
            if "rbtv_cover_art_landscape" in resources:
                url += "rbtv_cover_art_landscape"
            elif "rbtv_display_art_landscape" in resources:
                url += "rbtv_display_art_landscape"
            elif "rbtv_background_landscape" in resources:
                url += "rbtv_background_landscape"
            else:
                return None
        elif type == "banner":
            if "rbtv_cover_art_banner" in resources:
                url += "rbtv_cover_art_banner"
            elif "rbtv_display_art_banner" in resources:
                url += "rbtv_display_art_banner"
            else:
                return None
        elif type == "poster":
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
        details["summary"] = element.get("long_description") if element.get("long_description") and len(
            element.get("long_description")) > 0 else element.get("short_description")
        if element.get("resources"):
            details["landscape"] = self.get_image_url(element.get("id"), element.get("resources"), "landscape")
            details["fanart"] = self.get_image_url(element.get("id"), element.get("resources"), "landscape")
            details["banner"] = self.get_image_url(element.get("id"), element.get("resources"), "banner")
            details["thumb"] = self.get_image_url(element.get("id"), element.get("resources"), "thumb")
            details["poster"] = self.get_image_url(element.get("id"), element.get("resources"), "poster")

        # Strip out any keys with empty values
        return {k: v for k, v in details.iteritems() if v is not None}

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

        result = get_json(url+("?", "&")["?" in url]+"limit="+str(limit)+"&offset="+str((page-1)*limit), self.token)

        if 'links' in result:
            links = result["links"]
            for link in links:
                items.append(self.get_element_details(
                    link, PRODUCT))

        if 'collections' in result:
            collections = result["collections"]

            # Handle Search results
            if len(collections) > 0 and collections[0].get("collection_type") == "top_results":
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
