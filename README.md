[![Build Status](https://travis-ci.org/piejanssens/plugin.video.redbulltv.svg?branch=master)](https://travis-ci.org/piejanssens/plugin.video.redbulltv)

# Kodi Addon for Red Bull TV

Streaming video addon for Kodi that uses the Red Bull TV API.

This addon is based upon the work by [nedge2k](https://github.com/nedge2k/kodi.plugin.video.redbulltv2) and [andy-g](https://github.com/andy-g/kodi.plugin.video.redbulltv2)

## Contributing
Would you like to contribute and improve this add-on? Please do!
Please run the unit tests and pylinting checks before you submit your pull request.

### Unit Tests
To run the unit tests, run the folling from the root of this project:

```Shell
# bash/zsh
`python -B -m unittest discover`
```

### Pylint
To run pylint to check code style, run the folling from the root of this project:
	
```Shell
# bash/zsh
find . -iname "*.py" | xargs pylint --output-format=colorized --disable=line-too-long,wrong-import-position
```
