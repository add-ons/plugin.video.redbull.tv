import re, urllib, urllib2
import xml.etree.ElementTree as ET

def strip_url(url):
    nurl = re.search(r"\(\'(.*)\'\)", url)
    return nurl.group(1)

def build_url(base_url, query):
    return base_url + '?' + urllib.urlencode(query)

def get_xml(url):
    try:
        # response = urllib2.urlopen(url[0].decode('base64')+url[1])
        response = urllib2.urlopen(url)
    except urllib2.URLError:
        # xbmcgui.Dialog().ok("Error", "Error getting data from Redbull server: " + err.reason[1], "Try again shortly")
        raise
        # raise IOError("Error getting data from Redbull server: " + err.reason[1])
    else:
        return ET.parse(response)
