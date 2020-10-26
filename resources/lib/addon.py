# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
""" Addon code """

from __future__ import absolute_import, division, unicode_literals

import logging
from routing import Plugin

import xbmc
import xbmcgui
import xbmcplugin

import kodilogging
from kodiutils import addon_icon, addon_id, get_search_string, localize, play

kodilogging.config()
routing = Plugin()  # pylint: disable=invalid-name
_LOGGER = logging.getLogger('addon')
REDBULL_STREAMS = 'https://dms.redbull.tv/v3/'
REDBULL_API = 'https://api.redbull.tv/v3/'
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
    try:  # Python 3
        from urllib.error import URLError
        from urllib.request import Request, urlopen
    except ImportError:  # Python 2
        from urllib2 import Request, URLError, urlopen

    request = Request(url)
    if token:
        request.add_header('Authorization', token)
    try:
        response = urlopen(request)
    except URLError as exc:
        raise IOError(*exc.reason)

    from json import loads
    xbmc.log('Access: {url}'.format(url=url), xbmc.LOGNOTICE)
    return loads(response.read())


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
        item = xbmcgui.ListItem(path=REDBULL_STREAMS + "linear-borb/" + self.token + "/playlist.m3u8")
        xbmcplugin.setResolvedUrl(handle=self.addon_handle, succeeded=True, listitem=item)

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
            xbmcgui.Dialog().ok(localize(30220), localize(30221), localize(30222))
            return

        if not items:
            # No results found
            xbmcgui.Dialog().ok(localize(30223), localize(30224), localize(30225))
            return

        if items[0].get("event_date"):
            # Scheduled Event Time
            from time import timezone
            xbmcgui.Dialog().ok(localize(30226), localize(30227), items[0].get('event_date') + ' (GMT+' + str(timezone / 3600 * -1) + ')')
            return

        self.add_items(items)

        xbmc.executebuiltin('Container.SetViewMode({mode})'.format(mode=self.default_view_mode))
        xbmcplugin.endOfDirectory(self.addon_handle)

    def add_items(self, items):
        from urllib import urlencode
        for item in items:
            params = dict(api_url=item.get('url').encode('base64'))

            list_item = xbmcgui.ListItem(item.get("title"))
            list_item.setArt(dict(thumb=item.get('landscape', addon_icon())))

            if item.get('is_content'):
                params['is_stream'] = item['is_content']
                list_item.setProperty('IsPlayable', 'true')
            if 'fanart' in item:
                list_item.setArt(dict(fanart=item.get('fanart')))
            if 'landscape' in item:
                list_item.setArt(dict(landscape=item.get('landscape')))
            if 'banner' in item:
                list_item.setArt(dict(banner=item.get('banner')))
            if 'poster' in item:
                list_item.setArt(dict(poster=item.get('poster')))

            info_labels = dict(
                title=item.get('title'),
                plot=item.get('summary'),
                genre=item.get('subheading'),
                duration=item.get('duration'),
            )
            list_item.setInfo(type='Video', infoLabels=info_labels)
            nav_url = self.base_url + '?' + urlencode(params)
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=nav_url, listitem=list_item, isFolder=(not item["is_content"]))

    @staticmethod
    def play_stream(streams_url):
        play(streams_url)

    @staticmethod
    def get_image_url(element_id, resources, element_type, width=1024, quality=70):

        if element_type == 'fanart':
            if 'rbtv_background_landscape' in resources:
                image_type = 'rbtv_background_landscape'
            else:
                return None
        elif element_type == 'landscape':
            if 'rbtv_cover_art_landscape' in resources:
                image_type = 'rbtv_cover_art_landscape'
            elif 'rbtv_display_art_landscape' in resources:
                image_type = 'rbtv_display_art_landscape'
            elif "rbtv_background_landscape" in resources:
                image_type = 'rbtv_background_landscape'
            else:
                return None
        elif element_type == 'banner':
            if 'rbtv_cover_art_banner' in resources:
                image_type = 'rbtv_cover_art_banner'
            elif 'rbtv_display_art_banner' in resources:
                image_type = 'rbtv_display_art_banner'
            else:
                return None
        elif element_type == 'poster':
            if 'rbtv_cover_art_portrait' in resources:
                image_type = 'rbtv_cover_art_portrait'
            elif 'rbtv_display_art_portrait' in resources:
                image_type = 'rbtv_display_art_portrait'
            else:
                return None
        else:
            return None

        return 'https://resources.redbull.tv/{id}/{type}/im:i:w_{width},q_{quality}'.format(id=element_id, type=image_type, width=width, quality=quality)

    def get_element_details(self, element, element_type):
        details = {"is_content": False}
        if element.get("playable") or element.get("action") == "play":
            details["is_content"] = True
            details["url"] = REDBULL_STREAMS + element["id"] + "/" + self.token + "/playlist.m3u8"
            if element.get("duration"):
                details["duration"] = element.get("duration") / 1000
        # Handle video types that are actually upcoming events
        elif 'type' in element and element.get('type') == "video" and 'status' in element and element.get("status").get("label") == "Upcoming":
            details["event_date"] = element.get("status").get("start_time")
        elif element_type == COLLECTION:
            details["url"] = REDBULL_API + "collections/" + element["id"]  # + "?limit=20"
        elif element_type == PRODUCT:
            details["url"] = REDBULL_API + "products/" + element["id"]  # +"?limit=20"

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

        # If no url is specified, return the root menu
        if url is None:
            return [
                dict(title=localize(30010), url=REDBULL_STREAMS + 'linear-borb/' + self.token + '/playlist.m3u8', is_content=True),
                dict(title=localize(30011), url=REDBULL_API + 'products/discover', is_content=False),
                dict(title=localize(30012), url=REDBULL_API + 'products/channels', is_content=False),
                dict(title=localize(30013), url=REDBULL_API + 'products/events', is_content=False),
                dict(title=localize(30014), url=REDBULL_API + 'search?q=', is_content=False),
            ]

        result = get_json(url + ('?', '&')['?' in url] + 'limit=' + str(limit) + '&offset=' + str((page - 1) * limit), self.token)

        items = []
        if 'links' in result:
            links = result.get('links')
            for link in links:
                items.append(self.get_element_details(link, PRODUCT))

        if 'collections' in result:
            collections = result.get('collections')

            # Handle Search results
            if collections and collections[0].get('collection_type') == 'top_results':
                result['items'] = collections[0].get('items')
            else:
                for collection in collections:
                    items.append(self.get_element_details(collection, COLLECTION))

        if 'items' in result:
            result_items = result.get('items')
            for result_item in result_items:
                items.append(self.get_element_details(result_item, PRODUCT))

        return items
