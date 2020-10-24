# -*- coding: utf-8 -*-
""" Implementation of IPTVManager class """

from __future__ import absolute_import, division, unicode_literals

import logging
from collections import defaultdict
from datetime import datetime

from resources.lib import kodiutils
from resources.lib.addon import RedBullTV

_LOGGER = logging.getLogger(__name__)


class IPTVManager:
    """ Interface to IPTV Manager """

    def __init__(self, port):
        """ Initialize IPTV Manager object. """
        self.port = port

    def via_socket(func):  # pylint: disable=no-self-argument
        """ Send the output of the wrapped function to socket. """

        def send(self):
            """ Decorator to send data over a socket. """
            import json
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', self.port))
            try:
                sock.sendall(json.dumps(func(self)).encode())  # pylint: disable=not-callable
            finally:
                sock.close()

        return send

    @via_socket
    def send_channels(self):
        """ Return JSON-STREAMS formatted information to IPTV Manager. """

        streams = []

        streams.append(dict(
            name="Red Bull TV",
            stream="plugin://plugin.video.redbulltv/iptv/play",
            id="redbulltv",
            logo=kodiutils.get_addon_info("icon"),
            preset=88,
        ))

        return dict(version=1, streams=streams)

    @via_socket
    def send_epg(self):
        """ Return JSON-EPG formatted information to IPTV Manager. """
        epg = defaultdict(list)

        rb = RedBullTV()

        for item in rb.get_epg()['items']:
            epg['redbulltv'].append(dict(
                start=datetime.strptime(item['start_time'], "%Y-%m-%dT%H:%M:%S.%fZ").isoformat(),
                stop=datetime.strptime(item['end_time'], "%Y-%m-%dT%H:%M:%S.%fZ").isoformat(),
                title=item['title'],
                description=item['long_description'],
                subtitle=item['subheading'],
                episode=None,
                genre="Sport",
                image=rb.get_image_url(item['id'], item['resources'], "landscape"),
                date=None,
                stream=None
            ))

        return dict(version=1, epg=epg)
