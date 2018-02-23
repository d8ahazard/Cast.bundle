"""
Controller to interface with the Plex-app.
"""
import json
from time import sleep
from urlparse import urlparse

from pychromecast.controllers.media import MediaController

from . import BaseController
from ..config import APP_PLEX

STREAM_TYPE_UNKNOWN = "UNKNOWN"
STREAM_TYPE_BUFFERED = "BUFFERED"
STREAM_TYPE_LIVE = "LIVE"
MESSAGE_TYPE = 'type'

TYPE_PLAY = "PLAY"
TYPE_PAUSE = "PAUSE"
TYPE_STOP = "STOP"
TYPE_STEPFORWARD = "STEPFORWARD"
TYPE_STEPBACKWARD = "STEPBACK"
TYPE_PREVIOUS = "PREVIOUS"
TYPE_NEXT = "NEXT"
TYPE_LOAD = "LOAD"
TYPE_SEEK = "SEEK"
TYPE_MEDIA_STATUS = 'MEDIA_STATUS'
TYPE_GET_STATUS = "GET_STATUS"


class PlexController(MediaController):
    """ Controller to interact with Plex namespace. """

    def __init__(self):
        super(MediaController, self).__init__(
            "urn:x-cast:plex", "9AC194DC")

        self.app_id = "9AC194DC"
        self.namespace = "urn:x-cast:plex"
        self.request_id = 0
        self.media_session_id = 0
        self.receiver = None
        self.last_message = "No messages sent"
        self.media_meta = {}
        self.volume = 1
        self.muted = False
        self.stream_type=""
        self.state = "Idle"


    def set_volume(self, percent ,cast):
        percent = float(percent) / 100
        cast.set_volume(percent)

    def volume_up(self, cast):
        cast.volume_up()

    def volume_down(self, cast):
        cast.volume_down()

    def mute(self, cast, status):
        cast.set_volume_muted(status)

    def stop(self):
        self.namespace = "urn:x-cast:plex"
        """ Send stop command. """
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_STOP})

    def pause(self):
        self.namespace = "urn:x-cast:plex"
        """ Send pause command. """
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_PAUSE})

    def play(self):
        self.namespace = "urn:x-cast:plex"
        """ Send play command. """
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_PLAY})

    def previous(self):
        self.namespace = "urn:x-cast:plex"
        """ Send previous command. """
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_PREVIOUS})

    def next(self):
        self.namespace = "urn:x-cast:plex"
        """ Send next command. """
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_NEXT})

    def get_last_message(self):
        return self.last_message

    def play_media(self, item, type,callback_function=None):
        self.namespace = "urn:x-cast:plex"
        def app_launched_callback():
            self.logger.debug("Application is launched")
            self.set_load(item, type,callback_function)

        receiver_ctrl = self._socket_client.receiver_controller
        receiver_ctrl.launch_app(self.app_id,callback_function=app_launched_callback)

    def set_load(self, params,type,callback_function):
        self.logger.debug("Reached the load phase")
        self.namespace = "urn:x-cast:com.google.cast.media"
        playQueueID = params['Queueid']
        self.request_id += 1  # Update
        if (type == 'audio') | (type == 'group'):
            tv = True
        else:
            tv = False
        # TODO: Get the play queue type.
        o = urlparse(params['Serveruri'])
        protocol = o.scheme
        address = o.hostname
        port = o.port
        if protocol == 'https':
            verified = True
        else:
            verified = False

        self.logger.debug("Protocol, address, port and verified are %s %s %s and %s", protocol, address, port, verified)

        msg = {
          "type": "LOAD",
          "requestId": self.request_id,
          "sessionId": None,   #Does this need to be static?
          "media": {
            "contentId": params['Contentid'],
            "streamType": "BUFFERED",
              "metadata": None,
              "duration": None,
              "tracks": None,
              "textTrackStyle": None,
            "customData": {
              "playQueueType": params['Contenttype'],  #TODO: GET THIS RIGHT
              "providerIdentifier": "com.plexapp.plugins.library",
              "containerKey": "/playQueues/{}?own=1".format(playQueueID),
              "offset": int(params['Offset']),
              "directPlay": True,
              "directStream": True,
              "audioBoost": 100,
              "server": {
                "machineIdentifier": params["Serverid"],
                "transcoderVideo": True,
                "transcoderVideoRemuxOnly": False,
                "transcoderAudio": True,
                "version": "1.11.0.4666",
                "myPlexSubscription": True,
                "isVerifiedHostname": verified,
                "protocol": protocol,
                "address": address,
                "port": str(port),
                "accessToken": params["Token"]
              },
              "primaryServer": {
                "machineIdentifier": params["Serverid"],
                "transcoderVideo": True,
                "transcoderVideoRemuxOnly": False,
                "transcoderAudio": True,
                "version": "1.11.3.4803",
                "myPlexSubscription": True,
                "isVerifiedHostname": verified,
                "protocol": protocol,
                "address": address,
                "port": str(port),
                "accessToken": params["Token"]
              },
              "user": {
                "username": params["Username"]
              }
            }
          },
          "activeTrackIds":None,
          "autoplay": True,
          "currentTime": int(params['Offset']),
          "customData": None
        }
        self.logger.debug("(DH) Sending message: " + json.dumps(msg))

        def parse_status(data):
            self.update_plex_status(data)


        self.send_message(msg, inc_session_id=True,callback_function=parse_status)



    def update_plex_status(self,data):
        self.logger.debug("Got a request to update plex status: %s", json.dumps(data))
        self.media_meta = data['status'][0]['media']['metadata']
        self.volume = data['status'][0]['volume']['level']
        self.muted = data['status'][0]['volume']['muted']
        self.stream_type = data['status'][0]['customData']['type']
        self.state = data['status'][0]['playerState']


    def plex_status(self):
        self.namespace = "urn:x-cast:com.google.cast.media"
        self.logger.debug("Plex status requested.")

        def parseada_status(data):
            self.logger.debug("Callback fired?")
            self.update_plex_status(data)

        self.send_message({MESSAGE_TYPE: TYPE_GET_STATUS}, callback_function=parseada_status)

        sleep(1.0)

        return {
            "meta": self.media_meta,
            "volume": self.volume,
            "muted": self.muted,
            "type": self.stream_type,
            "state": self.state
        }



    def receive_message(self, message, data):
        """ Called when a media message is received. """
        if data[MESSAGE_TYPE] == TYPE_MEDIA_STATUS:
            self.logger.debug("(DH) MESSAGE RECEIVED: " + data)
            return True

        else:
            return False


    def _process_media_status(self, data):
        """ Processes a STATUS message. """
        self.status.update(data)

        self.logger.debug("MediaPC:Received status %s", data)
        self.raw_status = data
        # Update session active threading event
        if self.status.media_session_id is None:
            self.session_active_event.clear()
        else:
            self.session_active_event.set()

        self._fire_status_changed()

    def _fire_status_changed(self):
        """ Tells listeners of a changed status. """
        for listener in self._status_listeners:
            try:
                listener.new_media_status(self.status)
            except Exception:  # pylint: disable=broad-except
                pass



