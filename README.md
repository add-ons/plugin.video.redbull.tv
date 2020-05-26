[![Build Status](https://travis-ci.org/andy-g/kodi.plugin.video.redbulltv.svg?branch=add_tests_and_refactor)](https://travis-ci.org/andy-g/kodi.plugin.video.redbulltv)

# Kodi Addon for Red Bull TV

Streaming video addon for Kodi that uses the Red Bull TV API.

This addon is based upon the work by [nedge2k](https://github.com/nedge2k/kodi.plugin.video.redbulltv2) and [andy-g](https://github.com/andy-g/kodi.plugin.video.redbulltv2)

## Unit Tests
To run the unit tests (which includes integration tests that will connect to the Red Bull Server for content), navigate to the repository root and run the following:

```Shell
# bash/zsh
(cd plugin.video.redbulltv && python -B -m unittest discover)

# fish
pushd plugin.video.redbulltv; python -B -m unittest discover; popd
```

## Pylint
To run pylint to check code style, navigate to the repository root and run the following:

```Shell
find plugin.video.redbulltv -iname "*.py" | xargs pylint --output-format=colorized --disable=line-too-long,wrong-import-position
```
