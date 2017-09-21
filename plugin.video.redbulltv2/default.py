import sys, urlparse, os
import xbmcgui, xbmcplugin, xbmcaddon

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
        xbmcplugin.setContent(self.addon_handle, 'movies')
        self.redbulltv_client = redbulltv.RedbullTVClient()

    def navigation(self):
        url = self.args.get("api_url")[0].decode('base64') if self.args.get("api_url") else None
        category = self.args.get('category', [None])[0]

        items = self.redbulltv_client.get_items(url, category, self.addon.getSetting('video.resolution'))

        if items[0].get("is_stream"):
            self.play_stream(items[0])
        else:
            self.add_items(items)

        xbmcplugin.endOfDirectory(self.addon_handle)

    def add_items(self, items):
        for item in items:
            params = {'api_url' : item["url"].encode('base64')}
            if "category" in item:
                params['category'] = item["category"].encode('utf-8')

            url = utils.build_url(self.base_url, params)
            list_item = xbmcgui.ListItem(
                item.get("title"),
                iconImage='DefaultFolder.png',
                thumbnailImage=item.get("image", self.icon)
            )
            list_item.setInfo(type="Video", infoLabels={"Title": item["title"], "Plot": item.get("summary", None)})
            if item.get("is_content"):
                list_item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=(not item["is_content"]))

    def play_stream(self, item):
        list_item = xbmcgui.ListItem(label=item.get("title"), path=item.get("url"))
        list_item.setInfo(type="Video", infoLabels={"title": item.get("title"), "plot": item.get("summary")})
        list_item.setArt({'poster': item.get("image"), 'iconImage': "DefaultVideo.png", 'thumbnailImage': item.get("image")})
        list_item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(handle=self.addon_handle, succeeded=True, listitem=list_item)

RedbullTV2().navigation()
