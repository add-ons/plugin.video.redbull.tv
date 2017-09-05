import sys, re, urllib, urllib2, urlparse
import xml.etree.ElementTree as ET
import xbmcgui, xbmcplugin, xbmcaddon, xbmc

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

    @staticmethod
    def get_resolution_code(video_resolution_id):
        return {
            "0" : "320x180",
            "1" : "426x240",
            "2" : "640x360",
            "3" : "960x540",
            "4" : "1280x720",
        }.get(video_resolution_id, "1920x1080")

    def navigation(self):
        if self.args.get('function', None):
            self.get_listings()
        else:
            self.add_dir("listing", "Discover", self.redbull_api + "views/discover", self.icon)
            self.add_dir("listing", "TV", self.redbull_api + "views/tv", self.icon)
            self.add_dir("listing", "Channels", self.redbull_api + "views/channels", self.icon)
            self.add_dir("listing", "Calendar", self.redbull_api + "views/calendar", self.icon)
            self.add_dir("search", "Search", self.redbull_api + "search?q=", self.icon)
            xbmcplugin.endOfDirectory(self.addon_handle)

    def add_dir(self, function, category, api_url, image, subtitle='', summary='', is_folder=True):
        url = self.build_url({'function': function, 'category': category.encode('utf-8'), 'api_url' : api_url.encode('base64')})
        list_item = xbmcgui.ListItem(category + subtitle, iconImage='DefaultFolder.png', thumbnailImage=image)
        list_item.setInfo(type="Video", infoLabels={"Title": category + subtitle, "Plot": summary})
        if not is_folder:
            list_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=is_folder)

    def play_stream(self, content):
        list_item = xbmcgui.ListItem(label=content[0], path=content[2])
        list_item.setInfo(type="Video", infoLabels={"title": content[0], "plot": content[1]})
        list_item.setArt({'poster': content[3], 'iconImage': "DefaultVideo.png", 'thumbnailImage': content[3]})
        list_item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(handle=self.addon_handle, succeeded=True, listitem=list_item)

    def build_url(self, query):
        return self.base_url + '?' + urllib.urlencode(query)

    @staticmethod
    def strip_url(url):
        nurl = re.search(r"\(\'(.*)\'\)", url)
        return nurl.group(1)

    @staticmethod
    def get_keyboard(default="", heading="", hidden=False):
        keyboard = xbmc.Keyboard(default, heading, hidden)
        keyboard.doModal()
        if keyboard.isConfirmed():
            return str(urllib.quote_plus(keyboard.getText()))
        return default

    def get_content(self, data):
        name = data[0].find("title").text
        description = data[0].find("description").text
        image = data[0].find("image").get("src1080")
        url = data[0].find("mediaURL").text

        # Try find the specific stream based on the users preferences
        try:
            playlists = urllib2.urlopen(url).read()
            resolution_code = self.get_resolution_code(self.addon.getSetting('video.resolution'))
            media_url = re.search(
                "RESOLUTION=" + resolution_code + ".*\n(.*)",
                playlists).group(1)
        except Exception:
            xbmcgui.Dialog().ok("Error", "Couldn't find " + resolution_code + " stream", "Reverting to default quality")
        else:
            url = media_url

        return name, description, url, image

    @staticmethod
    def get_xml(url):
        try:
            response = urllib2.urlopen(url[0].decode('base64')+url[1])
        except urllib2.URLError as err:
            xbmcgui.Dialog().ok("Error", "Error getting data from Redbull server: " + err.reason[1], "Try again shortly")
            raise IOError("Error getting data from Redbull server: " + err.reason[1])
        else:
            return ET.parse(response)

    def build_list(self, array, function, url=''):
        for element in array:
            lurl = url
            if "onPlay" in element.attrib:
                lurl = self.strip_url(element.get("onPlay"))
            subtitle = ''
            if element.find('.//subtitle') is not None and element.find('.//subtitle').text is not None:
                subtitle = ' - ' + element.find('.//subtitle').text
            elif element.find('.//label2') is not None and element.find('.//label2').text is not None:
                subtitle = ' - ' + element.find('.//label2').text
            summary = ''
            if element.find('.//summary') is not None and element.find('.//summary').text is not None:
                summary = element.find('.//summary').text

            # if it's a content url, don't add it as a folder
            if re.search(self.redbull_api + "(content|linear_stream)", lurl):
                self.add_dir(function, self.get_label(element), lurl, self.get_image(element), subtitle, summary, False)
            else:
                self.add_dir(function, self.get_label(element), lurl, self.get_image(element), subtitle, summary)

    def get_image(self, element):
        if element.find('.//image') is not None:
            return element.find('.//image').get('src1080')

        return self.icon

    @staticmethod
    def get_label(element):
        if "accessibilityLabel" in element.attrib:
            return element.get("accessibilityLabel")
        elif element.find('.//label') is not None:
            return element.find('.//label').text

    def get_listings(self):
        function = self.args.get('function')[0]
        url = [self.args.get("api_url")[0], ""]

        if function == "search":
            url[1] = self.get_keyboard()
            function = "listing"

        try:
            xml = self.get_xml(url)
        except IOError:
            return

        data = {"showcasePoster": xml.findall('.//showcasePoster'),
                "sixteenByNinePoster": xml.findall('.//sixteenByNinePoster'),
                "actionButton": xml.findall(".//actionButton"),
                "twoLineMenuItem": xml.findall('.//twoLineMenuItem'),
                "twoLineEnhancedMenuItem": xml.findall('.//twoLineEnhancedMenuItem'),
                "collectionDivider": xml.findall('.//collectionDivider'),
                "shelf": xml.findall('.//shelf'),
                "httpLiveStreamingVideoAsset": xml.findall('.//httpLiveStreamingVideoAsset')}

        if function == "showcase":
            self.build_list(data['showcasePoster'], "content")

        if function == "content":
            if data["collectionDivider"]:
                function = "listing"
            else:
                if data["httpLiveStreamingVideoAsset"]:
                    self.play_stream(self.get_content(data["httpLiveStreamingVideoAsset"]))
                else:
                    for action_button in data["actionButton"]:
                        if action_button.attrib["id"] == "schedule-button":
                            self.add_dir("listing", action_button.get("accessibilityLabel"), self.strip_url(action_button.get("onPlay")), self.icon)
                    self.build_list(data['sixteenByNinePoster'], "content")
                    self.build_list(data['twoLineEnhancedMenuItem'], "content")

        if function == "collection":
            i = 0
            for collection in data['collectionDivider']:
                if collection.get("accessibilityLabel") == self.args.get('category')[0]:
                    self.build_list(data["shelf"][i].find('.//items').getchildren(), "content")
                i = i+1

        if function == "listing":
            if data["collectionDivider"]:
                if data["showcasePoster"]:
                    self.add_dir("showcase", "Showcase", url[0].decode('base64'), self.icon)
                self.build_list(data['collectionDivider'], "collection", url[0].decode('base64'))
            elif data["twoLineMenuItem"]:
                self.build_list(data['twoLineMenuItem'], "content")
            elif data["twoLineEnhancedMenuItem"]:
                self.build_list(data['twoLineEnhancedMenuItem'], "content", url[0].decode('base64'))

        xbmcplugin.endOfDirectory(self.addon_handle)
        #xbmcgui.Dialog().ok('hello',repr(len(data["collectionDivider"])))

RedbullTV2().navigation()
