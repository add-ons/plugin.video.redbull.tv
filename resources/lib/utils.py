import re, urllib, urllib2, json
import xml.etree.ElementTree as ET

def strip_url(url):
    nurl = re.search(r"\(\'(.*)\'\)", url)
    return nurl.group(1)

def build_url(base_url, query):
    return base_url + '?' + urllib.urlencode(query)

def get_xml(url):
    try:
        response = urllib2.urlopen(url)
    except urllib2.URLError as err:
        raise IOError(*err.reason)
    else:
        return ET.parse(response)

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
