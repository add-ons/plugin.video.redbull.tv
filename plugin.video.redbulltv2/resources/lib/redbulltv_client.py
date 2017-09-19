import sys, os, re, urllib2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
import utils

# python resources/lib/redbulltv.client.py
class RedbullTVClient(object):
    REDBULL_API = "https://appletv-v2.redbull.tv/"
    ROOT_MENU = [
        {"title": "Discover", "url": REDBULL_API + "views/discover", "is_content":False},
        {"title": "TV", "url": REDBULL_API + "views/tv", "is_content":False},
        {"title": "Channels", "url": REDBULL_API + "views/channels", "is_content":False},
        {"title": "Calendar", "url": REDBULL_API + "views/calendar", "is_content":False}
    ]

    def get_resolution_code(self, video_resolution_id):
        return {
            "0" : "320x180",
            "1" : "426x240",
            "2" : "640x360",
            "3" : "960x540",
            "4" : "1280x720",
        }.get(video_resolution_id, "1920x1080")

    def get_stream_details(self, element, resolution_id=None):
        name = element.find("title").text
        description = element.find("description").text
        image = element.find("image").get("src1080")
        url = element.find("mediaURL").text

        # Try find the specific stream based on the users preferences
        try:
            playlists = urllib2.urlopen(url).read()
            resolution = self.get_resolution_code(resolution_id)
            media_url = re.search(
                "RESOLUTION=" + resolution + ".*\n(.*)",
                playlists).group(1)
        except Exception:
            print "Couldn't find " + resolution + " stream", "Reverting to default quality"
        else:
            url = media_url

        return {"title":name, "url":url, "summary":description, "image": image, "is_stream":True}

    def get_element_details(self, element, url=None):
        details = {"title":None, "url":url, "is_content":False}

        # Get title
        if "accessibilityLabel" in element.attrib:
            details["title"] = element.get("accessibilityLabel")
        elif element.find('.//label') is not None:
            details["title"] = element.find('.//label').text

        # Get subtitle
        if element.find('.//subtitle') is not None:
            details["subtitle"] = ' - ' + element.find('.//subtitle').text
        elif element.find('.//label2') is not None:
            details["subtitle"] = ' - ' + element.find('.//label2').text

        # Get summary
        if element.find('.//summary') is not None:
            details["summary"] = element.find('.//summary').text

        # Get url
        if "onPlay" in element.attrib:
            details["url"] = utils.strip_url(element.get("onPlay"))
            
            if re.search(self.REDBULL_API + "(content|linear_stream)", details["url"]):
              details["is_content"] = True
        
        # Get image
        if element.find('.//image') is not None:
            details["image"] = element.find('.//image').get('src1080')

        if url == details["url"]:
            details["category"] = details["title"]

        return details

    def get_items(self, url=None, category=None, resolution_id=None):
        # If no url is specified, return the root menu
        if url is None:
            return self.ROOT_MENU

        xml = utils.get_xml(url)
        items = []
        
        # if the current url is a media stream
        if xml.find('.//httpLiveStreamingVideoAsset') is not None:
            items.append(self.get_stream_details(xml.find('.//httpLiveStreamingVideoAsset'), resolution_id))
        # if no category is specified, find the categories or item collection
        elif category is None:
            data = {
                "collectionDividers": xml.findall('.//collectionDivider'),
            }
            # Show Categories if relevant
            if data["collectionDividers"]:
                for collection in xml.findall('.//showcase') + data["collectionDividers"]:
                    items.append(self.get_element_details(collection, url))
            else:
                for item in xml.findall('.//twoLineMenuItem') + xml.findall('.//twoLineEnhancedMenuItem') + xml.findall('.//sixteenByNinePoster') + xml.findall('.//actionButton'):
                    items.append(self.get_element_details(item))
        # if a category is specified, find the items for the specified category
        elif category is not None:
            if category == 'Featured':
                for item in xml.findall('.//showcasePoster'):
                    items.append(self.get_element_details(item))
            else:
                i = 0
                for collection in xml.findall('.//collectionDivider'):
                    if collection.get("accessibilityLabel") == category:
                        for item in xml.findall('.//shelf')[i].find('.//items').getchildren():
                            items.append(self.get_element_details(item))
                    i = i + 1

        return items