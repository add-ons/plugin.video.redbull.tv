# -*- coding: utf-8 -*-
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
""" Addon code """

from __future__ import absolute_import, division, unicode_literals

import logging
import routing

from xbmc import executebuiltin, log
from xbmcgui import ListItem, Dialog
from xbmcplugin import addDirectoryItem, endOfDirectory, setContent

import kodilogging
from kodiutils import addon_icon, addon_id, get_search_string, localize, play, TitleItem, get_addon_info, show_listing

from redbull import RedBullTV

kodilogging.config()
routing = routing.Plugin()  # pylint: disable=invalid-name
redbull = RedBullTV()

_LOGGER = logging.getLogger('addon')
COLLECTION = 1
PRODUCT = 2

@routing.route('/')
def index():
    """ Show the main menu """
    log('Building main menu')
    listing = [
        TitleItem(
            title=localize(30010),  # A-Z
            path=routing.url_for(iptv_play),
            art_dict=dict(
                icon='DefaultMovieTitle.png',
                fanart=get_addon_info('fanart'),
                poster=addon_icon()
            ),
            info_dict=dict(
                plot='Best of Red Bull TV',
            ),
            is_playable=True
        ),
        TitleItem(
            title=localize(30011),  # A-Z
            path=routing.url_for(browse_product, 'discover'),
            art_dict=dict(
                icon='DefaultMovieTitle.png',
                fanart=get_addon_info('fanart'),
                poster=addon_icon()
            )
        ),
        TitleItem(
            title=localize(30012),  # A-Z
            path=routing.url_for(browse_collection, 'playlists::d554f1ca-5a8a-4d5c-a562-419185d57979'),
            art_dict=dict(
                icon='DefaultMovieTitle.png',
                fanart=get_addon_info('fanart'),
                poster=addon_icon()
            )
        ),
        TitleItem(
            title=localize(30013),  # A-Z
            path=routing.url_for(browse_product, 'events'),
            art_dict=dict(
                icon='DefaultMovieTitle.png',
                fanart=get_addon_info('fanart'),
                poster=addon_icon()
            )
        ),
        TitleItem(
            title=localize(30014),  # A-Z
            path=routing.url_for(search),
            art_dict=dict(
                icon='DefaultMovieTitle.png',
                fanart=get_addon_info('fanart'),
                poster=addon_icon()
            )
        )
    ]

    show_listing(listing, sort=['unsorted'])


@routing.route('/iptv/play')
def iptv_play():
    play_uid('linear-borb')


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


@routing.route('/play/<uid>')
def play_uid(uid):
    play(redbull.get_play_url(uid))


@routing.route('/collection/<uid>')
def browse_collection(uid):
    build_menu(redbull.get_collection_url(uid))


@routing.route('/product/<uid>')
def browse_product(uid):
    build_menu(redbull.get_product_url(uid))


@routing.route('/notify/<msg>')
def notify(msg):
    Dialog().ok(msg)


@routing.route('/search')
def search():
    query = get_search_string()
    if query:
        build_menu(redbull.get_search_url(query))


def build_menu(items_url):
    setContent(routing.handle, 'videos')
    list_items = []

    try:
        content = redbull.get_content(items_url)
    except IOError:
        # Error getting data from Redbull server
        Dialog().ok(localize(30220), localize(30221), localize(30222))
        return

    if content.get('links'):
        for link in content.get('links'):
            list_items.append(generate_list_item(link, PRODUCT))

    if content.get('collections'):
        for collection in content.get('collections'):
            if collection.get('collection_type') == 'top_results':
                content['items'] = collection.get('items')
            else:
                list_items.append(generate_list_item(collection, COLLECTION))

    if content.get('items'):
        for item in content.get('items'):
            list_items.append(generate_list_item(item, PRODUCT))

    if not list_items:
        Dialog().ok(localize(30223), localize(30224), localize(30225))
        return

    for list_item in list_items:
        addDirectoryItem(handle=routing.handle, url=list_item.getPath(), listitem=list_item, isFolder=(not '/play/' in list_item.getPath()))

    executebuiltin('Container.SetViewMode({mode})'.format(mode=55)) # Wide List
    endOfDirectory(routing.handle)


def generate_list_item(element, element_type):
    list_item = ListItem(element.get('title'))
    info_labels = dict(title=element.get('title'))
    uid = element.get('id')
    resources = element.get('resources')

    if element.get('playable') or element.get('action') == 'play':
        list_item.setPath(routing.url_for(play_uid, uid=uid))
        list_item.setProperty('IsPlayable','true')
        if element.get('duration'):
            info_labels['duration'] = element.get('duration') / 1000
    elif element.get('type') == 'video' and element.get('status').get('label') == 'Upcoming':
        info_labels['premiered'] = element.get('status').get('start_time')
        from time import timezone
        list_item.setPath('/notify/' + localize(30026), localize(30027), element.get('event_date') + ' (GMT+' + str(timezone / 3600 * -1))
    elif element_type == COLLECTION:
        list_item.setPath(routing.url_for(browse_collection, uid=uid))
    elif element_type == PRODUCT:
        list_item.setPath(routing.url_for(browse_product, uid=uid))

    info_labels['title'] = element.get('label') or element.get('title')
    info_labels['genre'] = element.get('subheading')
    info_labels['plot'] = element.get('long_description') if element.get('long_description') else element.get('short_description')

    if resources:
        list_item.setArt(dict(fanart=redbull.get_image_url(uid, resources, 'landscape')))
        list_item.setArt(dict(landscape=redbull.get_image_url(uid, resources, 'landscape')))
        list_item.setArt(dict(banner=redbull.get_image_url(uid, resources, 'banner')))
        list_item.setArt(dict(poster=redbull.get_image_url(uid, resources, 'poster')))
        list_item.setArt(dict(thumb=redbull.get_image_url(uid, resources, 'thumb')))

    if list_item.getArt('thumb') is None:
        list_item.setArt(dict(thumb=addon_icon()))

    list_item.setInfo(type='Video', infoLabels=info_labels)

    return list_item


def run(params):
    """ Run the routing plugin """
    routing.run(params)
