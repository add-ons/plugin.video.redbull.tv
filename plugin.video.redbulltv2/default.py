import sys, urllib, urllib2, urlparse, xbmcgui, xbmcplugin, re
import xml.etree.ElementTree as ET

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'movies')
redbull_api = " https://appletv-v2.redbull.tv/"

def navigation():
	addDir("listing","Discover",redbull_api + "views/discover")
	addDir("listing","TV",redbull_api + "views/tv")
	addDir("listing","Channels",redbull_api + "views/channels")
	addDir("listing","Calendar",redbull_api + "views/calendar")
	xbmcplugin.endOfDirectory(addon_handle)
	
def addDir(function,category,api_url):
	url = build_url({'function': function, 'category': category.encode('utf-8'), 'api_url' : api_url.encode('base64')})
	li = xbmcgui.ListItem(category, iconImage='DefaultFolder.png')
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
	
def addStream(content):
	li = xbmcgui.ListItem(content[0], iconImage="DefaultVideo.png", thumbnailImage=content[3])
	li.setInfo( type="Video", infoLabels={ "Title": content[0], "Plot": content[1]} )
	xbmcplugin.addDirectoryItem(handle=addon_handle, url=content[2], listitem=li, isFolder=False)
	
def build_url(query):
	return base_url + '?' + urllib.urlencode(query)
	
def strip_url(url):
	nurl = re.search("\(\'(.*)\'\)",url)
	return nurl.group(1)
	
def getContent(data):
	name = data[0].find("title").text
	description = data[0].find("description").text
	url = data[0].find("mediaURL").text
	image = data[0].find("image").get("src1080")
	return name, description, url, image
	
def getXML(url):
	try:
		response = urllib2.urlopen(url.decode('base64'))
	except urllib2.URLError as e:
		xbmcgui.Dialog().ok("Error","Error getting data from Redbull server: " + e.reason[1],"Try again shortly")
		raise IOError("Error getting data from Redbull server: " + e.reason[1])
	else:
		return ET.parse(response)
	
def getListings(url,function,category):
	try:
		xml = getXML(url)
	except IOError as e:
		return
		
	data = { "showcasePoster" : xml.findall('.//showcasePoster'),
			"sixteenByNinePoster" : xml.findall('.//sixteenByNinePoster'),
			"actionButton" : xml.findall(".//actionButton"),
			"twoLineMenuItem" : xml.findall('.//twoLineMenuItem'),
			"twoLineEnhancedMenuItem" : xml.findall('.//twoLineEnhancedMenuItem'),
			"collectionDivider" : xml.findall('.//collectionDivider'),
			"shelf" : xml.findall('.//shelf'),
			"httpLiveStreamingVideoAsset" : xml.findall('.//httpLiveStreamingVideoAsset')}

	if function == "showcase":
		for showcase in data['showcasePoster']:
				addDir("content",showcase.get("accessibilityLabel"),strip_url(showcase.get("onPlay")))
	
	if function == "content":
		if len(data["collectionDivider"]) > 0:
			function = "listing"
		else:
			if len(data["httpLiveStreamingVideoAsset"]) > 0:
				content = getContent(data["httpLiveStreamingVideoAsset"])
				addStream(content)
			else:
				#xbmcgui.Dialog().ok("Info","No stream available (yet)")
				for actionButton in data["actionButton"]:
					if actionButton.attrib["id"] == "schedule-button":
						addDir("listing",actionButton.get("accessibilityLabel"),strip_url(actionButton.get("onPlay")))
				for related in data["sixteenByNinePoster"]:
					addDir("content",related.get("accessibilityLabel"),strip_url(related.get("onPlay")))
				for listing in data["twoLineEnhancedMenuItem"]:
					addDir("content",listing.find("label").text,strip_url(listing.get("onPlay")))
			
	if function == "collection":
		i = 0;
		for collection in data['collectionDivider']:
			if collection.get("accessibilityLabel") == category:
				for poster in data["shelf"][i].find('.//items').getchildren():
					addDir("content",poster.get("accessibilityLabel"),strip_url(poster.get("onPlay")))
			i = i+1
			
	if function == "listing":
		if len(data["collectionDivider"]) > 0:
			if len(data["showcasePoster"]) > 0:
				addDir("showcase","Showcase",url.decode('base64'))
			for collection in data['collectionDivider']:
				addDir("collection",collection.get("accessibilityLabel"),url.decode('base64'))
		elif len(data["twoLineMenuItem"]) > 0:
			for tv in data["twoLineMenuItem"]:
				addDir("content",tv.find("label").text,strip_url(tv.get("onPlay")))
		elif len(data["twoLineEnhancedMenuItem"]) > 0:
			for schedule in data["twoLineEnhancedMenuItem"]:
				if "onPlay" in schedule.attrib:
					addDir("content",schedule.find("label").text,strip_url(schedule.get("onPlay")))
				
	xbmcplugin.endOfDirectory(addon_handle)
	#xbmcgui.Dialog().ok('hello',repr(len(data["collectionDivider"])))			
	
function = args.get('function', None)
category = args.get('category', None)
api_url = args.get('api_url', None)

if function is None:
	navigation()
else:
	getListings(api_url[0],function[0],category[0])