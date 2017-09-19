import sys, re, urllib, urllib2, urlparse, os
import xml.etree.ElementTree as ET
import xbmcgui, xbmcplugin, xbmcaddon, xbmc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources'))
import lib.utils as utils
import lib.redbulltv_client as redbulltv

class RedbullTV2(object):
    def __init__(self):
        self.id = 'plugin.video.redbulltv2'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.base_url = sys.argv[0]
        self.addon_handle = int(sys.argv[1])
        self.args = urlparse.parse_qs(sys.argv[2][1:])
        self.redbull_api = "https://appletv-v2.redbull.tv/"
        xbmcplugin.setContent(self.addon_handle, 'movies')
        self.redbulltv_client = redbulltv.RedbullTVClient()

    def navigation(self):
        print 'in navigation'
        url, category = None, None
        if self.args.get("api_url",None):
            url = self.args.get("api_url")[0].decode('base64')
            category = self.args.get('category',[None])[0]
        
        items = self.redbulltv_client.get_items(url, category, self.addon.getSetting('video.resolution'))

        if items[0].get("is_stream", False):
            self.play_stream(items[0])
        else:
            self.add_items(items)

        xbmcplugin.endOfDirectory(self.addon_handle)

    def add_items(self, items):
        for item in items:
            qs = {'api_url' : item["url"].encode('base64')}
            if "category" in item:
                qs['category'] = item["category"].encode('utf-8')

            url = utils.build_url(self.base_url, qs)
            list_item = xbmcgui.ListItem(
                item["title"] + item.get("subtitle",""), 
                iconImage='DefaultFolder.png', 
                thumbnailImage=item.get("image", self.icon)
            )
            list_item.setInfo(type="Video", infoLabels={"Title": item["title"] + item.get("subtitle",""), "Plot": item.get("summary",None)})
            if "is_content" in item:
                list_item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=(item["is_content"]) == False)

    def play_stream(self, item):
        list_item = xbmcgui.ListItem(label=item.get("title"), path=item.get("url"))
        list_item.setInfo(type="Video", infoLabels={"title": item.get("title"), "plot": item.get("summary")})
        list_item.setArt({'poster': item.get("image"), 'iconImage': "DefaultVideo.png", 'thumbnailImage': item.get("image")})
        list_item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(handle=self.addon_handle, succeeded=True, listitem=list_item)

RedbullTV2().navigation()
