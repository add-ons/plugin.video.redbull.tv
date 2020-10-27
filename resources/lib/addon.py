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

from redbull import RedBullTV

kodilogging.config()
routing = Plugin()  # pylint: disable=invalid-name

_LOGGER = logging.getLogger('addon')
COLLECTION = 1
PRODUCT = 2

redbull = RedBullTV()

@routing.route('/')
def show_main_menu():
    """ Show the main menu """
    _LOGGER.debug('Building main menu')
    _LOGGER.info('Building main menu')
    _LOGGER.warning('Building main menu')

    main_menu = [
        dict(title=localize(30010), url=routing.url_for(iptv_play)),
        dict(title=localize(30011), url=routing.url_for(browse_product, 'discover')),
        dict(title=localize(30012), url=routing.url_for(browse_product, 'channels')),
        dict(title=localize(30013), url=routing.url_for(browse_product, 'events')),
        dict(title=localize(30014), url=routing.url_for(search))
    ]

    for item in main_menu:
        list_item = xbmcgui.ListItem(item.get('title'))
        xbmcplugin.addDirectoryItem(routing.handle, url=item.get('url'), listitem=list_item, isFolder=(not 'play' in item.get('url')))

    xbmcplugin.endOfDirectory(routing.handle)


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
    xbmcgui.Dialog().ok(msg)


@routing.route('/search')
def search():
    query = get_search_string()
    if query:
        build_menu(redbull.get_search_url(query))


def build_menu(items_url):
    xbmcplugin.setContent(routing.handle, 'videos')
    list_items = []

    try:
        content = redbull.get_content(items_url)
    except IOError:
        # Error getting data from Redbull server
        xbmcgui.Dialog().ok(localize(30220), localize(30221), localize(30222))
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
        xbmcgui.Dialog().ok(localize(30223), localize(30224), localize(30225))
        return

    for list_item in list_items:
        xbmcplugin.addDirectoryItem(handle=routing.handle, url=list_item.getPath(), listitem=list_item, isFolder=(not '/play/' in list_item.getPath()))

    xbmc.executebuiltin('Container.SetViewMode({mode})'.format(mode=55)) # Wide List
    xbmcplugin.endOfDirectory(routing.handle)


def generate_list_item(element, element_type):
    list_item = xbmcgui.ListItem(element.get('title'))
    info_labels = dict(title=element.get('title'))

    if element.get('playable') or element.get('action') == 'play':
        list_item.setPath(routing.url_for(play_uid, uid=element['id']))
        if element.get('duration'):
            info_labels['duration'] = element.get('duration') / 1000
    elif element.get('type') == 'video' and element.get('status').get('label') == 'Upcoming':
        info_labels['premiered'] = element.get('status').get('start_time')
        from time import timezone
        list_item.setPath('/notify/' + localize(30026), localize(30027), element.get('event_date') + ' (GMT+' + str(timezone / 3600 * -1))
    elif element_type == COLLECTION:
        list_item.setPath(routing.url_for(browse_collection, uid=element['id']))
    elif element_type == PRODUCT:
        list_item.setPath(routing.url_for(browse_product, uid=element['id']))

    info_labels['title'] = element.get('label') or element.get('title')
    info_labels['genre'] = element.get('subheading')
    info_labels['plot'] = element.get('long_description') if element.get('long_description') else element.get('short_description')

    if element.get('resources'):
        list_item.setArt(dict(fanart=redbull.get_image_url(element.get('id'), element.get('resources'), 'landscape')))
        list_item.setArt(dict(landscape=redbull.get_image_url(element.get('id'), element.get('resources'), 'landscape')))
        list_item.setArt(dict(banner=redbull.get_image_url(element.get('id'), element.get('resources'), 'banner')))
        list_item.setArt(dict(poster=redbull.get_image_url(element.get('id'), element.get('resources'), 'poster')))
        list_item.setArt(dict(thumb=redbull.get_image_url(element.get('id'), element.get('resources'), 'thumb')))

    if list_item.getArt('thumb') is None:
        list_item.setArt(dict(thumb=addon_icon()))

    list_item.setInfo(type='Video', infoLabels=info_labels)

    return list_item


def run(params):
    """ Run the routing plugin """
    routing.run(params)
