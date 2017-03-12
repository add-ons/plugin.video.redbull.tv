# 2017 Redbull TV Plugin for Kodi
Streaming video plugin for Kodi that uses the Redbull TV Apple TV v2 XML "API" - it's not really an API, more like an XML web page that gets displayed as-is and then styled with css on Apple TV units. This is when the listing in Kodi will look a bit "odd".

This is the first time I've written anything in Python so it may be a little rough around the edges but it seems to work well enough for my needs.

Changelog:

	0.0.1
		Initial Release
		
	0.0.2
		Fixed issue with scheduled event streams not appearing in lists
		Added plugin icon/fanart
		
	0.0.3
		Fixed compatibility issue with Kodi forks (like SPMC) using python 2.6
		Added error handling for when the server url errors out
