import sys, urllib, urllib2, urlparse, xbmcgui, xbmcplugin, xbmcaddon, re, xbmc
import xml.etree.ElementTree as ET

class RedbullTV2():
	def __init__(self):
		self.id = 'plugin.video.redbulltv2'
		self.addon = xbmcaddon.Addon(self.id)
		self.icon = self.addon.getAddonInfo('icon')
		self.base_url = sys.argv[0]
		self.addon_handle = int(sys.argv[1])
		self.args = urlparse.parse_qs(sys.argv[2][1:])
		self.redbull_api = " https://appletv-v2.redbull.tv/"
		xbmcplugin.setContent(self.addon_handle, 'movies')

	@staticmethod
	def getResolutionCode(id):
		return {
			"0" : "320x180",
			"1" : "426x240",
			"2" : "640x360",
			"3" : "960x540",
			"4" : "1280x720",
		}.get(id, "1920x1080")

	def navigation(self):
		if self.args.get('function', None):
			self.getListings()
		else:
			self.addDir("listing","Discover",self.redbull_api + "views/discover",self.icon)
			self.addDir("listing","TV",self.redbull_api + "views/tv",self.icon)
			self.addDir("listing","Channels",self.redbull_api + "views/channels",self.icon)
			self.addDir("listing","Calendar",self.redbull_api + "views/calendar",self.icon)
			self.addDir("search","Search",self.redbull_api + "search?q=",self.icon)
			xbmcplugin.endOfDirectory(self.addon_handle)

	def addDir(self,function,category,api_url,image,subtitle='', summary=''):
		url = self.build_url({'function': function, 'category': category.encode('utf-8'), 'api_url' : api_url.encode('base64')})
		li = xbmcgui.ListItem(category + subtitle, iconImage='DefaultFolder.png', thumbnailImage=image)
		li.setInfo( type="Video", infoLabels={ "Title": category + subtitle, "Plot": summary} )
		xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=li, isFolder=True)

	def addStream(self,content):
		li = xbmcgui.ListItem(content[0], iconImage="DefaultVideo.png", thumbnailImage=content[3])
		li.setInfo( type="Video", infoLabels={ "Title": content[0], "Plot": content[1]} )
		xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=content[2], listitem=li, isFolder=False)

	def build_url(self,query):
		return self.base_url + '?' + urllib.urlencode(query)

	@staticmethod
	def strip_url(url):
		nurl = re.search("\(\'(.*)\'\)",url)
		return nurl.group(1)

	@staticmethod
	def getKeyboard( default="", heading="", hidden=False ):
		keyboard = xbmc.Keyboard( default, heading, hidden )
		keyboard.doModal()
		if ( keyboard.isConfirmed() ):
			return str(urllib.quote_plus(keyboard.getText()))
		return default

	def getContent(self,data):
		name = data[0].find("title").text
		description = data[0].find("description").text
		image = data[0].find("image").get("src1080")
		url = data[0].find("mediaURL").text

		# Try find the specific stream based on the users preferences
		try:
			playlists = urllib2.urlopen(url).read()
			# media_url = re.search("x" + self.resolutions[self.addon.getSetting('video.resolution')] + ",.*\n(.*)",response).group(1)
			resolutionCode = self.getResolutionCode(self.addon.getSetting('video.resolution'))
			media_url = re.search(
				"RESOLUTION=" + resolutionCode + ",.*\n(.*)",
				playlists).group(1)
		except urllib2.URLError as e:
			xbmcgui.Dialog().ok("Error","Couldn't find " + resolutionCode + " stream: " + e.reason[1],"Reverting to default quality")
		else:
			url = media_url

		return name, description, url, image

	@staticmethod
	def getXML(url):
		try:
			response = urllib2.urlopen(url[0].decode('base64')+url[1])
		except urllib2.URLError as e:
			xbmcgui.Dialog().ok("Error","Error getting data from Redbull server: " + e.reason[1],"Try again shortly")
			raise IOError("Error getting data from Redbull server: " + e.reason[1])
		else:
			return ET.parse(response)

	def buildList(self,array,function,url=''):
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
			if element.find('.//summary') is not None and element.find('.//summary').text is not None :
				summary = element.find('.//summary').text
			self.addDir(function,self.getLabel(element),lurl,self.getImage(element),subtitle,summary)

	def getImage(self,element):
		if element.find('.//image') is not None:
			return element.find('.//image').get('src1080')
		else:
			return self.icon

	@staticmethod
	def getLabel(element):
		if "accessibilityLabel" in element.attrib:
			return element.get("accessibilityLabel")
		elif element.find('.//label') is not None:
			return element.find('.//label').text

	def getListings(self):
		function = self.args.get('function')[0]
		url = [self.args.get("api_url")[0],""]

		if function == "search":
			url[1] = self.getKeyboard()
			function = "listing"

		try:
			xml = self.getXML(url)
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
			self.buildList(data['showcasePoster'],"content")

		if function == "content":
			if len(data["collectionDivider"]) > 0:
				function = "listing"
			else:
				if len(data["httpLiveStreamingVideoAsset"]) > 0:
					self.addStream(self.getContent(data["httpLiveStreamingVideoAsset"]))
				else:
					for actionButton in data["actionButton"]:
						if actionButton.attrib["id"] == "schedule-button":
							self.addDir("listing",actionButton.get("accessibilityLabel"),self.strip_url(actionButton.get("onPlay")),self.icon)
					self.buildList(data['sixteenByNinePoster'],"content")
					self.buildList(data['twoLineEnhancedMenuItem'],"content")

		if function == "collection":
			i = 0;
			for collection in data['collectionDivider']:
				if collection.get("accessibilityLabel") == self.args.get('category')[0]:
					self.buildList(data["shelf"][i].find('.//items').getchildren(),"content")
				i = i+1

		if function == "listing":
			if len(data["collectionDivider"]) > 0:
				if len(data["showcasePoster"]) > 0:
					self.addDir("showcase","Showcase",url[0].decode('base64'),self.icon)
				self.buildList(data['collectionDivider'],"collection",url[0].decode('base64'))
			elif len(data["twoLineMenuItem"]) > 0:
				self.buildList(data['twoLineMenuItem'],"content")
			elif len(data["twoLineEnhancedMenuItem"]) > 0:
				self.buildList(data['twoLineEnhancedMenuItem'],"content",url[0].decode('base64'))

		xbmcplugin.endOfDirectory(self.addon_handle)
		#xbmcgui.Dialog().ok('hello',repr(len(data["collectionDivider"])))

RedbullTV2().navigation()
