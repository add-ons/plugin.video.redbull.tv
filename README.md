[![Build Status](https://travis-ci.org/andy-g/kodi.plugin.video.redbulltv2.svg?branch=add_tests_and_refactor)](https://travis-ci.org/andy-g/kodi.plugin.video.redbulltv2)

# 2017 Redbull TV Plugin for Kodi
Streaming video plugin for Kodi that uses the Redbull TV Apple TV v2 XML "API" - it's not really an API, more like an XML web page that gets displayed as-is and then styled with css on Apple TV units. This is when the listing in Kodi will look a bit "odd".

This addon is based on the initial work done by nedge2k: https://github.com/nedge2k/kodi.plugin.video.redbulltv2.

## Changelog:

- **0.0.1**  
	Initial Release
	
- **0.0.2**  
	Fixed issue with scheduled event streams not appearing in lists  
	Added plugin icon/fanart
		
- **0.0.3**  
	Fixed compatibility issue with Kodi forks (like SPMC) using python 2.6  
	Added error handling for when the server url errors out
	
- **0.0.4**  
	Code cleanup/refactoring  
	Added thumbnailimage and summary to directories
	
- **0.0.5**  
	Added search function

- **0.1.0**  
	Moved RedbullTV functionality into a RedbullTV2 Client  
	Add settings to specify preferred video resolution  
	Added Unit Tests  
	Added Integration Tests  
	Added Continuous Integration with Travis CI  

## Unit Tests
To run the unit tests (which includes integration tests that will connect to the Redbull Server for content), navigate to the repository root and run the following:

```Shell
# bash/zsh
(cd plugin.video.redbulltv2 && python -B -m unittest discover)

# fish
pushd plugin.video.redbulltv2; python -B -m unittest discover; popd
```

## Pylint
To run pylint to check code style, navigate to the repository root and run the following:
	
```Shell
find plugin.video.redbulltv2 -iname "*.py" | xargs pylint --output-format=colorized --disable=line-too-long,wrong-import-position
```
