############################################################################
# This plugin will allow external calls, that the plugin can then handle
# See TODO doc for more details
#
# Made by
# dane22....A Plex Community member
#
############################################################################

# To find Work in progress, search this file for the word

from __future__ import print_function

import pychromecast
from datetime import datetime, date

from pychromecast.controllers.plex import PlexController
from pychromecast.controllers.media import MediaController
import time
import json

#Dummy Imports
#from Framework.api.objectkit import ObjectContainer, DirectoryObject
#from Framework.docutils import Plugin, HTTP, Log, Request
#from Framework.docutils import Data



NAME = 'FlexTV'
VERSION = '1.1.100'
PREFIX = '/applications/FlexTV'
ICON = 'icon-default.png'


# Start function
def Start():
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    ObjectContainer.title1 = NAME + VERSION
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = 0

def UpdateCache():
    Log.Debug("UpdateCache called")
    fetch_devices()

@handler(PREFIX, NAME, thumb=ICON)
@route(PREFIX + '/MainMenu')
def MainMenu():
    """
    Main menu
    """
    Log.Debug("**********  Starting MainMenu  **********")
    title = NAME + VERSION
    # TODO: Build that list of cast devices and show them here?
    oc = ObjectContainer(
        title1=title,
        no_cache=True,
        no_history=True)
    Log.Debug("**********  Ending MainMenu  **********")
    return oc


@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
    """
    Called by the framework every time a user changes the prefs
    We add this dummy function, to avoid errors in the log
    """
    return


@route(PREFIX + '/Devices')
def Devices():
    """
    Endpoint to scan LAN for cast devices
    """
    Log.Debug('Recieved a call to fetch devices')
    casts = fetch_devices()
    count = len(casts)
    Log.Debug("Found " + str(count) + " cast devices!")

    oc = ObjectContainer(
        title1="Cast Devices",
        no_cache=True,
        no_history=True)

    for cast in casts:
        oc.add(DirectoryObject(
            title=cast['name'],
            duration=cast['status'],
            tagline=cast['appId'],
            summary=cast['type'],
            thumb=cast['uri']
        ))

    return oc


@route(PREFIX + '/Play')
def Play():
    """
    Endpoint to play media.

    Sends to "urn:x-cast:com.google.cast.media", with JSON,
    after verifying that the Plex app is running on cast device


    Needed params in request headers:
    uri
    requestId
    contentType
    offset
    serverId
    transcoderVideo
    serverUri
    username

    """

    Log.Debug('Recieved a call to play media.')
    # client_uri = unicode(Request.Headers('uri')).split(":")
    # host = client_uri[0]
    # port = client_uri[1]
    # request_id = unicode(Request.Headers('requestid'))
    # content_id = unicode(Request.Headers('contentId')) + '?own=1&window=200'  # key
    # content_type = unicode(Request.Headers('contentType'))
    # offset = unicode(Request.Headers('offset'))
    # server_id = unicode(Request.Headers('serverId'))
    # transcoder_video = unicode(Request.Headers('transcoderVideo'))
    # server_uri = unicode(Request.headers('serverUri')).split("://")
    # server_parts = server_uri[1].split(":")
    # server_protocol = server_uri[0]
    # server_ip = server_parts[0]
    # server_port = server_parts[1]
    #
    # username = unicode(Request.Headers('username'))
    # true = "true"
    # false = "false"
    # requestArray = {
    #     "type": 'LOAD',
    #     'requestId': request_id,
    #     'media': {
    #         'contentId': content_id,
    #         'streamType': 'BUFFERED',
    #         'contentType': content_type,
    #         'customData': {
    #             'offset': offset,
    #             'directPlay': true,
    #             'directStream': true,
    #             'subtitleSize': 100,
    #             'audioBoost': 100,
    #             'server': {
    #                 'machineIdentifier': server_id,
    #                 'transcoderVideo': transcoder_video,
    #                 'transcoderVideoRemuxOnly': false,
    #                 'transcoderAudio': true,
    #                 'version': '1.4.3.3433',
    #                 'myPlexSubscription': true,
    #                 'isVerifiedHostname': true,
    #                 'protocol': server_protocol,
    #                 'address': server_ip,
    #                 'port': server_port,
    #                 'user': {
    #                     'username': username
    #                 }
    #             },
    #             'containerKey': content_id
    #         },
    #         'autoplay': true,
    #         'currentTime': 0
    #     }
    # }
    #
    # try:
    #     cast = pychromecast.Chromecast(host,port)
    # except pychromecast.ChromecastConnectionError:
    #     Log.Debug('Error connecting to host.')
    # else:
    #     cast.wait()
    #     status = cast.status
    #     mc = MediaController()
    #     cast.register_handler(mc)
    #     string = json.dumps(requestArray)
    #     mc.send_message(string)
    oc = ObjectContainer(
        title1='Status',
        no_cache=True,
        no_history=True)
    return oc


@route(PREFIX + '/Cmd')
def Cmd():
    """
    Media control command(s).

    Plex-specific commands use the format:

    Required params:
    client (FriendlyName)
    command - see below

    Where <COMMAND> is one of:
    PLAY (resume)
    PAUSE
    STOP
    STEPFORWARD
    STEPBACK (BACKWARD? Need to test, not in PHP cast app)
    PREVIOUS
    NEXT
    MUTE
    UNMUTE
    VOLUME - also requires an int representing level from 0-100

    Volume commands don't require the plex controller...
    But we could possibly put them in there just to make it a one-stop shop...

    """
    Log.Debug('Recieved a call to control playback')
    chromecasts = fetch_devices()
    client = unicode(Request.Headers["client"])
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == client)
    command = unicode(Request.Headers["command"])
    Log.Debug('Params are %s' % client % ' and ' % command)
    if len(cast) != 0:
        cast.wait()
        if command == "VOLUME":
            level = unicode(Request.Headers["level"])
            Log.Debug('Trying to set volume to ' % level)
            mc = cast.media_controller
            # TODO: Send the volume command, dude.
        if (command == "MUTE") | (command == "UNMUTE"):
            mc = cast.media_controller
            # TODO: Mute/unmute
        else:
            d = PlexController()
            cast.register_handler(d)
            message = PlexFunction(command)
            Log.Debug('Formatted Plex message is %s' % message)
            d.send_message(message)

    response = 'Params are %s' % client % ' and ' % command
    # Create a dummy container to return, in order to make
    # the framework happy
    # Can be used if needed to get a return value, by replacing title var with
    # what you want to return
    oc = ObjectContainer(
        title1=response,
        no_cache=True,
        no_history=True)
    return oc


@route(PREFIX + '/Status')
def Status():
    """
    Fetch player status
    "urn:x-cast:com.google.cast.media", '{"type":"GET_STATUS", "requestId":1}'

    Then filter for "/{\"type.*/"

    """
    Log.Debug('Trying to get cast device status here')

    chromecasts = pychromecast.get_chromecasts()
    client = unicode(Request.Headers["client"])
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == client)
    Log.Debug('Params are %s' % client)
    if len(cast) != 0:
        # TODO: Convert status to json or something?
        status = cast.status
    else:
        status = "No matching device."
    # Create a dummy container to return, in order to make
    # the framework happy
    # Can be used if needed to get a return value, by replacing title var with
    # what you want to return
    oc = ObjectContainer(
        title1=status,
        no_cache=True,
        no_history=True)
    return oc


def PlexFunction(command):
    return {
        'PLAY': "{MESSAGE_TYPE: TYPE_PLAY}",
        'PAUSE': "{MESSAGE_TYPE: TYPE_PAUSE}",
        'STOP': "{MESSAGE_TYPE: TYPE_STOP}",
        'STEPBACKWARD': "{MESSAGE_TYPE: TYPE_STEPBACKWARD}",
        'STEPFORWARD': "{MESSAGE_TYPE: TYPE_STEPFORWARD}",
        'BACK': "{MESSAGE_TYPE: TYPE_BACK}",
        'NEXT': "{MESSAGE_TYPE: TYPE_NEXT}"
    }[command]

def fetch_devices():
    rescan = False
    if Data.Exists('last_fetch'):
        lf = Data.LoadObject('last_fetch')
        now = datetime.now()
        fmt = '%Y-%m-%d %H:%M:%S'
        diff = getTimeDifferenceFromNow(lf,now)
    else:
        now = datetime.now()
        Data.SaveObject('last_fetch',now)
        diff = 120

    has_devices = Data.Exists('device_json')

    if (has_devices == False) | (diff >= 20):
        Log.Debug("Re-fetching devices")
        now = datetime.now()
        casts = pychromecast.get_chromecasts(2, None, None, True)
        data_array = []
        for cast in casts:
            cast_item = {
                "uri":cast.uri,
                "name":cast.name,
                "status":cast.is_idle,
                "type":cast.cast_type,
                "appId":cast.app_id
            }
            data_array.append(cast_item)


        if len(data_array) != 0:
            Log.Debug("Found me some cast devices.")
            cast_string = JSON.StringFromObject(data_array)
            Data.Save('device_json',cast_string)
            Data.SaveObject('last_fetch', now)

        casts = data_array
    else:
        casts_string = Data.Load('device_json')
        casts = JSON.ObjectFromString(casts_string)

    return casts

def getTimeDifferenceFromNow(TimeStart, TimeEnd):
    timeDiff = TimeEnd - TimeStart
    return timeDiff.total_seconds() / 60