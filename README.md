[![GitHub release](https://img.shields.io/github/release/add-ons/plugin.video.redbulltv.svg)](https://github.com/add-ons/plugin.video.redbulltv/releases)
[![Build status](https://github.com/add-ons/plugin.video.redbulltv/workflows/CI/badge.svg)](https://github.com/add-ons/plugin.video.redbulltv/actions)
[![Codecov status](https://img.shields.io/codecov/c/github/add-ons/plugin.video.redbulltv/master)](https://codecov.io/gh/add-ons/plugin.video.redbulltv/branch/master)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-yellow.svg)](https://opensource.org/licenses/GPL-3.0)
[![Contributors](https://img.shields.io/github/contributors/add-ons/plugin.video.redbulltv.svg)](https://github.com/add-ons/plugin.video.redbulltv/graphs/contributors)

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

## Releases
### v3.1.0
- IPTV Manager support

### v3.0.0
- Harder, Better, Faster, Stronger

### v2.0.2 (2018-01-12)

### v2.0.1 (2017-10-22)

### v2.0.0 (2017-10-21)

### v0.0.5 (2017-04-13)
- Added search function

### v0.0.4 (2017-03-23)
- Packaged update
- Code cleanup, directory icons

### v0.0.3 (2017-03-12)
- See changelog in README

### v0.0.2 (2017-03-11)
- Added some polish, fixed an issue with scheduled events

### v0.0.1 (2017-03-11)
- Basic working plugin
