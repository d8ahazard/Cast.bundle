"""
Controller to interface with the Plex-app.
"""
from . import BaseController

MESSAGE_TYPE = 'type'

TYPE_PLAY = "PLAY"
TYPE_PAUSE = "PAUSE"
TYPE_STOP = "STOP"
TYPE_STEPFORWARD = "STEPFORWARD"
TYPE_STEPBACKWARD = "STEPBACK"
TYPE_PREVIOUS = "PREVIOUS"
TYPE_NEXT = "NEXT"


class PlexController(BaseController):
    """ Controller to interact with Plex namespace. """

    def __init__(self):
        super(PlexController, self).__init__(
            "urn:x-cast:plex", "9AC194DC")

    def play(self):
        """ Send play command. """
        self.send_message({MESSAGE_TYPE: TYPE_PLAY})

    def pause(self):
        """ Send pause command. """
        self.send_message({MESSAGE_TYPE: TYPE_PAUSE})

    def stop(self):
        """ Send stop command. """
        self.send_message({MESSAGE_TYPE: TYPE_STOP})

    def stepforward(self):
        """ Send play command. """
        self.send_message({MESSAGE_TYPE: TYPE_STEPFORWARD})

    def stepbackward(self):
        """ Send stop command. """
        self.send_message({MESSAGE_TYPE: TYPE_STEPBACKWARD})

    def previous(self):
        """ Send stop command. """
        self.send_message({MESSAGE_TYPE: TYPE_PREVIOUS})

    def next(self):
        """ Send stop command. """
        self.send_message({MESSAGE_TYPE: TYPE_NEXT})







