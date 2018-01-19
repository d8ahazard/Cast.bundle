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

import threading
from datetime import datetime

import pychromecast
from pychromecast.controllers.plex import PlexController
from pychromecast.controllers.media import MediaController

from CustomObject import MediaContainer, DeviceContainer


# Dummy Imports
# import Framework.context
# from Framework.api.objectkit import ObjectContainer, DirectoryObject
# from Framework.docutils import Plugin, HTTP, Log, Request
# from Framework.docutils import Data


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
    HTTP.CacheTime = 5
    time = 5 * 60
    UpdateCache()
    threading.Timer(time, UpdateCache).start()


# This doesn't actually ever seem to run, so we're gonna call a threading timer...
def UpdateCache():
    Log.Debug("UpdateCache called")
    scan_devices()


@handler(PREFIX, NAME, thumb=ICON)
@route(PREFIX + '/MainMenu')
def MainMenu():
    casts = fetch_devices()

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
    for cast in casts:
        oc.add(DirectoryObject(
            title=cast['name'],
            duration=cast['status'],
            tagline=cast['uri'],
            summary=cast['type']
        ))

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
    # Grab our response header?
    casts = fetch_devices()

    mc = MediaContainer()
    for cast in casts:
        dc = DeviceContainer(cast)
        mc.add(dc)

    return mc


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
            Log.Debug('Trying to set volume to %s' % level)
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

    response = 'Params are %s and %s', client, command
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
    TODO: Figure out how to parse and return additional data here

    """
    uri = "FOOBAR"
    name = "FOOBAR"
    cc = []
    Log.Debug('Trying to get cast device status here')
    for key, value in Request.Headers.items():
        Log.Debug("Header key %s is %s", key, value)
        if key in ("X-Plex-Clienturi", "Clienturi"):
            Log.Debug("We have a client URI")
            uri = value

        if key in ("X-Plex-Clientname", "Clientname"):
            Log.Debug("X-Plex-Clientname: " + value)
            name = value

    chromecasts = fetch_devices()
    for chromecast in chromecasts:
        if chromecast['name'] == name:
            Log.Debug("Found a matching chromecast: " + name)
            cc = chromecast
        if chromecast['uri'] == uri:
            Log.Debug("Found a matching uri:" + uri)
            cc = chromecast

    if len(cc) != 0:
        Log.Debug("We have set a chromecast here.")
        uris = cc['uri'].split(":")
        host = uris[0]
        port = uris[1]
        Log.Debug("Host and port are %s and %s", host, port)
        cc = pychromecast.Chromecast(host, int(port))
        Log.Debug("Waiting for device")
        # cc.wait()
        Log.Debug("Device is here!")
        if cc.is_idle != True:
            Log.Debug("We have a non-idle cast")
            status = "Running" + cc.app_display_name()
        else:
            status = "Idle"

    else:
        status = "No matching device."

    if uri == name:
        status = "No device specified"
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


def fetch_devices(rescan=False):

    has_devices = Data.Exists('device_json')
    if has_devices == False:
        Log.Debug("No cached data exists, re-scanning.")
        casts = scan_devices()

    else:
        Log.Debug("Returning cached data")
        casts_string = Data.Load('device_json')
        casts = JSON.ObjectFromString(casts_string)

    return casts

# Scan our devices and save them to cache.
# This should NEVER be called from an endpoint...we don't have the time

def scan_devices():
    Log.Debug("Re-fetching devices")
    casts = pychromecast.get_chromecasts(2, None, None, True)
    data_array = []
    for cast in casts:
        cast_item = {
            "uri": cast.uri,
            "name": cast.name,
            "status": cast.is_idle,
            "type": cast.cast_type,
            "appId": cast.app_id
        }
        data_array.append(cast_item)

    Log.Debug("Item count is " + str(len(data_array)))
    cast_string = JSON.StringFromObject(data_array)
    Data.Save('device_json', cast_string)

    return data_array


def getTimeDifferenceFromNow(TimeStart, TimeEnd):
    timeDiff = TimeEnd - TimeStart
    return timeDiff.total_seconds() / 60
