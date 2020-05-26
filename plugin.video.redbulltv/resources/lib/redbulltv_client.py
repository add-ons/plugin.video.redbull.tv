import re, urllib2, os
import resources.lib.utils as utils
import web_pdb #web_pdb.set_trace()

class RedbullTVClient(object):

    token = utils.get_json("https://api.redbull.tv/v3/session?category=smart_tv&os_family=android")["token"]

    REDBULL_STREAMS = "https://dms.redbull.tv/v3/"
    REDBULL_API = "https://api.redbull.tv/v3/"
    ROOT_MENU = [
        {"title": "Live TV", "url": REDBULL_STREAMS + "linear-borb/" + token + "/playlist.m3u8", "is_content": True},
        {"title": "Discover", "url": REDBULL_API + "products/discover", "is_content":False},
        {"title": "Browse", "url": REDBULL_API + "products/channels", "is_content":False},
        {"title": "Events", "url": REDBULL_API + "products/events", "is_content":False},
        {"title": "Search", "url": REDBULL_API + "search?q=", "is_content":False},
    ]
    ELEMENT_TYPE = {"collection": 1, "product": 2}
  
    def __init__(self, resolution=None):
        self.resolution = resolution

    @staticmethod
    def get_resolution_code(video_resolution_id):
        return {
            "0" : "320x180",
            "1" : "426x240",
            "2" : "640x360",
            "3" : "960x540",
            "4" : "1280x720",
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

            resolution = self.get_resolution_code(self.resolution)
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

        url+= "/im"

        if width:
            url += ":i:w_1024"

        if quality:
            url += ",q_70"

        return url

    def get_element_details(self, element, element_type):
        details = {"is_content":False}
        if element.get("playable") or element.get("action") == "play":
            details["is_content"] = True
            details["url"] = self.REDBULL_STREAMS + element["id"] + "/" + self.token + "/playlist.m3u8"
            if element.get("duration"):
                details["duration"] = element.get("duration") / 1000
        # Handle video types that are actually upcoming events
        elif 'type' in element and element.get('type') == "video" and 'status' in element and element.get("status").get("label") == "Upcoming":
            details["event_date"] = element.get("status").get("start_time")
        elif element_type == self.ELEMENT_TYPE["collection"]:
            details["url"] = self.REDBULL_API + "collections/" + element["id"] # + "?limit=20"
        elif element_type == self.ELEMENT_TYPE["product"]:
            details["url"] = self.REDBULL_API + "products/" + element["id"] #+"?limit=20"
        subtitle = element.get("subheading")

        details["title"] = (element.get("label") or element.get("title")) + ((" - " + subtitle) if subtitle else "")
        details["summary"] = element.get("long_description") if element.get("long_description") and len(element.get("long_description")) > 0 else element.get("short_description")
        if element.get("resources"):
            #web_pdb.set_trace()
            details["landscape"] = self.get_image_url(element.get("id"), element.get("resources"), "landscape")
            details["fanart"] = self.get_image_url(element.get("id"), element.get("resources"), "landscape")
            details["banner"] = self.get_image_url(element.get("id"), element.get("resources"), "banner")
            details["thumb"] = self.get_image_url(element.get("id"), element.get("resources"), "thumb")
            details["poster"] = self.get_image_url(element.get("id"), element.get("resources"), "poster")

        # Strip out any keys with empty values
        return {k:v for k, v in details.iteritems() if v is not None}

    def get_items(self, url=None, page=1, limit=20):

        items = []

        # If no url is specified, return the root menu
        if url is None:
            return self.ROOT_MENU

        result = utils.get_json(url+("?", "&")["?" in url]+"limit="+str(limit)+"&offset="+str((page-1)*limit), self.token)

        if 'links' in result:
            links = result["links"]
            for link in links:
                items.append(self.get_element_details(link, self.ELEMENT_TYPE["product"]))
        
        if 'collections' in result:
            collections = result["collections"]

            # Handle Search results
            if len(collections) > 0 and collections[0].get("collection_type") == "top_results":
                result["items"] = collections[0]["items"]
            else:
                for collection in collections:
                    items.append(self.get_element_details(collection, self.ELEMENT_TYPE["collection"]))

        if 'items' in result:
            result_items = result["items"]
            for result_item in result_items:
                items.append(self.get_element_details(result_item, self.ELEMENT_TYPE["product"]))

        # Add next item if meta.total > meta.offset + meta.limit
        # print("client result count: "+str(len(items)))

        return items
