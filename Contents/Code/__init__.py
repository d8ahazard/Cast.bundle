############################################################################
# This plugin will allow external calls, that the plugin can then handle
# See TODO doc for more details
#
# Made by
# dane22 & digitalhigh....Plex Community members
#
############################################################################

# To find Work in progress, search this file for the word

from __future__ import print_function

import base64
import glob
import threading
import time
import json

import xml.etree.ElementTree as ET

import os
import config

import StringIO
from subzero.lib.io import FileIO
from zipfile import ZipFile, ZIP_DEFLATED

import pychromecast
from pychromecast.controllers.media import MediaController
from pychromecast.controllers.plex import PlexController

import log_helper
from CustomContainer import MediaContainer, DeviceContainer, CastContainer, ZipObject

# Dummy Imports for PyCharm

# import Framework.context
# from Framework.api.objectkit import ObjectContainer, DirectoryObject
# from Framework.docutils import Plugin, HTTP, Log, Request
# from Framework.docutils import Data

NAME = 'Cast'
VERSION = '1.1.102'
PREFIX = '/applications/Cast'
PREFIX2 = '/chromecast'
APP = '/chromecast'
ICON = 'icon-cast.png'
ICON_CAST = 'icon-cast.png'
ICON_CAST_AUDIO = 'icon-cast_audio.png'
ICON_CAST_VIDEO = 'icon-cast_video.png'
ICON_CAST_GROUP = 'icon-cast_group.png'
ICON_CAST_REFRESH = 'icon-cast_refresh.png'
ICON_PLEX_CLIENT = 'icon-plex_client.png'
TEST_CLIP = 'test.mp3'


# Start function
def Start():
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = 5
    if Data.Exists('device_json') is not True: UpdateCache()
    ValidatePrefs()
    CacheTimer()


def CacheTimer():
    mins = 10
    time = mins * 60
    Log.Debug("Cache timer started, updating in %s minutes",mins)
    threading.Timer(time, CacheTimer).start()
    UpdateCache()


# This doesn't actually ever seem to run, so we're gonna call a threading timer...
def UpdateCache():
    Log.Debug("UpdateCache called")
    scan_devices()


@handler(PREFIX, NAME)
@handler(PREFIX2, NAME)
@route(PREFIX + '/MainMenu')
@route(PREFIX2)
def MainMenu(Rescanned=False):
    casts = fetch_devices()

    """
    Main menu
    """
    Log.Debug("**********  Starting MainMenu  **********")
    title = NAME + " - " + VERSION
    if Data.Exists('last_scan'): title = NAME + " - " + Data.Load('last_scan')
    # TODO: Build that list of cast devices and show them here?
    oc = ObjectContainer(
        title1=title,
        no_cache=True,
        no_history=True,
        title_bar="Chromecast",
        view_group="Details")

    if Rescanned is True:
        oc.message = "Rescan complete!"

    #
    do = DirectoryObject(
        title="Rescan Devices",
        thumb=R(ICON_CAST_REFRESH),
        key=Callback(Rescan))

    oc.add(do)

    do = DirectoryObject(
        title="Devices",
        thumb=R(ICON_CAST),
        key=Callback(Resources))

    oc.add(do)

    do = DirectoryObject(
        title="Broadcast",
        thumb=R(ICON_CAST_AUDIO),
        key=Callback(Broadcast))

    oc.add(do)

    return oc


@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():
    """
    Called by the framework every time a user changes the prefs
    We add this dummy function, to avoid errors in the log
    and stuff.
    """

    dependencies = ['pychromecast']
    log_helper.register_logging_handler(dependencies, level="DEBUG")
    return


@route(APP + '/devices')
@route(PREFIX2 + '/devices')
def Devices():
    """

    Endpoint to scan LAN for cast devices
    """
    Log.Debug('Recieved a call to fetch cast devices')
    # Grab our response header?
    casts = fetch_devices()
    mc = MediaContainer()
    for cast in casts:
        Log.Debug("Cast type is " + cast['type'])
        if (cast['type'] == 'cast') | (cast['type'] == 'audio') | (cast['type'] == 'group'):
            dc = CastContainer(cast)
            mc.add(dc)

    return mc


@route(APP + '/clients')
@route(PREFIX2 + '/clients')
def Clients():
    """
    Endpoint to scan LAN for cast devices
    """
    Log.Debug('Recieved a call to fetch all devices')
    # Grab our response header?
    casts = fetch_devices()

    mc = MediaContainer()
    for cast in casts:
        dc = CastContainer(cast)
        mc.add(dc)

    return mc


@route(APP + '/resources')
@route(PREFIX2 + '/resources')
def Resources():
    """
    Endpoint to scan LAN for cast devices
    """
    Log.Debug('Recieved a call to fetch devices')
    # Grab our response header?
    casts = fetch_devices()

    oc = ObjectContainer(
        no_cache=True,
        no_history=True,
        view_group="Details")

    for cast in casts:
        type = cast['type']
        icon = ICON_CAST
        if type == "audio": icon = ICON_CAST_AUDIO
        if type == "cast": icon = ICON_CAST_VIDEO
        if type == "group": icon = ICON_CAST_GROUP
        if cast['app'] == "Plex Client": icon = ICON_PLEX_CLIENT
        Log.Debug("Type is %s",type)
        do = DirectoryObject(
            title=cast['name'],
            duration=cast['status'],
            tagline=cast['uri'],
            summary=cast['app'],
            key=Callback(Status, input=cast['name']),
            thumb=R(icon))
        oc.add(do)

    return oc


@route(APP + '/rescan')
def Rescan():
    """
    Endpoint to scan LAN for cast devices
    """
    Log.Debug('Recieved a call to rescan devices')
    # Grab our response header?
    UpdateCache()
    return MainMenu(True)


@route(PREFIX + '/logs')
@route(PREFIX2 + '/logs')
def DownloadLogs():
    buff = StringIO.StringIO()
    zip_archive = ZipFile(buff, mode='w', compression=ZIP_DEFLATED)
    paths = get_log_paths()
    if (paths[0] is not False) & (paths[1] is not False):
        logs = sorted(glob.glob(paths[0] + '*')) + [paths[1]]
        for path in logs:
            Log.Debug("Trying to read path: " + path)
            data = StringIO.StringIO()
            data.write(FileIO.read(path))
            zip_archive.writestr(os.path.basename(path), data.getvalue())

        zip_archive.close()

        return ZipObject(buff.getvalue())

    Log.Debug("No log path found, foo.")
    return ObjectContainer(
        no_cache=True,
        title1="No logs found",
        no_history=True,
        view_group="Details")


@route(APP + '/play')
def Play():
    """
    Endpoint to play media.
    """
    Log.Debug('Recieved a call to play media.')
    params = ['Uri', 'Requestid', 'Contentid', 'Contenttype', 'Offset', 'Serverid', 'Serveruri',
              'Username', "Token", "Queueid"]
    values = sort_headers(params, True)
    status = "Missing required headers"
    msg = status
    if values is not False:
        Log.Debug("Holy crap, we have all the headers we need.")
        client_uri = values['Uri'].split(":")
        host = client_uri[0]
        port = int(client_uri[1])
        pc = False
        msg = "No message received"
        try:
            cast = pychromecast.Chromecast(host, port)
            cast.wait()
            type = cast.cast_type
            pc = PlexController()
            cast.register_handler(pc)
            pc.play_media(values, type)
            #msg = base64.b64encode(str(cast.media_controller.status))
            #cast.disconnect()


        except pychromecast.LaunchError, pychromecast.PyChromecastError:
            Log.Debug('Error connecting to host.')
            status = "Error"
        finally:
            if pc is not False:
                status = "Success"

    oc = MediaContainer({
        'Name': 'Playback Status',
        'Status': status,
        'Message': msg
    })

    return oc


@route(APP + '/cmd')
def Cmd():
    """
    Media control command(s).

    Plex-specific commands use the format:


    Required params:
    Uri
    Cmd
    Vol(If setting volume, otherwise, ignored)

    Where <COMMAND> is one of:
    PLAY (resume)
    PAUSE
    STOP
    STEPFORWARD
    STEPBACKWARD Need to test, not in PHP cast app)
    PREVIOUS
    NEXT
    MUTE
    UNMUTE
    VOLUME - also requires an int representing level from 0-100

    """
    Log.Debug('Recieved a call to control playback')
    chromecasts = fetch_devices()
    params = sort_headers(['Uri', 'Cmd', 'Val'])
    status = "Missing paramaters"
    response = "Error"

    if params is not False:
        uri = params['Uri'].split(":")
        cast = pychromecast.Chromecast(uri[0], int(uri[1]))
        cast.wait()
        pc = PlexController()
        Log.Debug("Handler namespace is %s" % pc.namespace)
        cast.register_handler(pc)

        Log.Debug("Handler namespace is %s" % pc.namespace)

        cmd = params['Cmd']
        Log.Debug("Command is " + cmd)

        if cmd == "play": pc.play()
        if cmd == "pause": pc.pause()
        if cmd == "stop": pc.stop()
        # if cmd == "stepforward": pc.stepforward()
        if cmd == "stepbakward": pc.stepbackward()
        if cmd == "next": pc.next()
        if cmd == "offset": pc.seek(params["Val"])
        # TODO: See if we can make plexcontroller find it's registered cast automagically
        if cmd == "previous": pc.previous()
        if cmd == "mute": pc.mute(cast, True)
        if cmd == "unmute": pc.mute(cast, False)
        if cmd == "volume": pc.set_volume(params["Val"])
        if cmd == "voldown": pc.volume_down(cast)
        if cmd == "volup": pc.volume_up(cast)
        #status = str(cast.media_controller.status)
        #status = base64.b64encode(status)
        #Log.Debug("Status received: " + status)
        cast.disconnect()
        response = "Command successful"
    # Create a dummy container to return, in order to make
    # the framework happy
    # Can be used if needed to get a return value, by replacing title var with
    # what you want to return
    oc = ObjectContainer(
        title1=response,
        title2=status,
        no_cache=True,
        no_history=True)
    return oc


@route(APP + '/audio')
def Audio():
    """
    Endpoint to play media.

    """

    Log.Debug('Recieved a call to play an audio clip.')
    params = ['Uri', 'Path']
    values = sort_headers(params, True)
    status = "Missing required headers"
    if values is not False:
        Log.Debug("Holy crap, we have all the headers we need.")
        client_uri = values['Uri'].split(":")
        host = client_uri[0]
        port = int(client_uri[1])
        path = values['Path']
        try:
            cast = pychromecast.Chromecast(host, port)
            cast.wait()
            mc = cast.media_controller
            mc.play_media(path, 'audio/mp3')
        except pychromecast.LaunchError, pychromecast.PyChromecastError:
            Log.Debug('Error connecting to host.')
        finally:
            Log.Debut("We have a cast")
            status = "Playback successful"

    oc = ObjectContainer(
        title1=status,
        no_cache=True,
        no_history=True)

    return oc


@route(APP + '/broadcast/test')
def Test():
    values = {'Path': R(TEST_CLIP)}
    status = "Test failed."
    casts = fetch_devices()
    try:
        for cast in casts:
            if cast['type'] == "audio":
                mc = MediaController()
                Log.Debug("We should be broadcasting to " + cast['name'])
                uri = cast['uri'].split(":")
                cast = pychromecast.Chromecast(uri[0], int(uri[1]))
                cast.wait()
                cast.register_handler(mc)
                mc.play_media(values['Path'], 'audio/mp3')


    except pychromecast.LaunchError, pychromecast.PyChromecastError:
        Log.Debug('Error connecting to host.')
    finally:
        Log.Debug("We have a cast")
    status = "Test successful!"

    oc = ObjectContainer(
        title1=status,
        no_cache=True,
        no_history=True)

    return oc


@route(APP + '/broadcast')
def Broadcast():
    Log.Debug('Recieved a call to broadcast an audio clip.')
    params = ['Path']
    values = sort_headers(params, True)
    status = "No clip specified"
    if values is not False:
        do = False
        casts = fetch_devices()
        disconnect = []
        controllers = []
        try:

            for cast in casts:
                if cast['type'] == "audio":
                    mc = MediaController()
                    Log.Debug("We should be broadcasting to " + cast['name'])
                    uri = cast['uri'].split(":")
                    cast = pychromecast.Chromecast(uri[0], int(uri[1]))
                    cast.wait()
                    cast.register_handler(mc)
                    controllers.append(mc)
                    disconnect.append(cast)

            for mc in controllers:
                mc.play_media(values['Path'], 'audio/mp3')

        except pychromecast.LaunchError, pychromecast.PyChromecastError:
            Log.Debug('Error connecting to host.')
        finally:
            for cast in disconnect:
                cast.disconnect()
            Log.Debug("We have a cast")

    else:
        do = DirectoryObject(
            title='Test Broadcast',
            tagline="Send a test broadcast to audio devices.",
            key=Callback(Test))
        status = "Foo"

    oc = ObjectContainer(
        title1=status,
        no_cache=True,
        no_history=True)

    if do is not False: oc.add(do)

    return oc


@route(APP + '/status')
@route(APP + '/resources/status')
def Status(input=False):
    """
    Fetch player status
    TODO: Figure out how to parse and return additional data here

    """
    uri = "FOOBAR"
    name = "FOOBAR"
    cc = []
    showAll = False
    Log.Debug('Trying to get cast device status here')
    for key, value in Request.Headers.items():
        Log.Debug("Header key %s is %s", key, value)
        if key in ("X-Plex-Clienturi", "Clienturi"):
            Log.Debug("We have a client URI")
            uri = value

        if key in ("X-Plex-Clientname", "Clientname"):
            Log.Debug("X-Plex-Clientname: " + value)
            name = value

    if input is not False: name = input
    if uri == name: showAll = True

    chromecasts = fetch_devices()
    devices = []

    for chromecast in chromecasts:
        cc = False
        if showAll is not True:
            if chromecast['name'] == name:
                Log.Debug("Found a matching chromecast: " + name)
                cc = chromecast

            if chromecast['uri'] == uri:
                Log.Debug("Found a matching uri:" + uri)
                cc = chromecast
        else:
            cc = chromecast

        if cc is not False:
            devices.append(cc)

    oc = ObjectContainer(
        title1="Status",
        no_cache=True,
        no_history=True)

    if len(devices) != 0:
        for device in devices:
            Log.Debug("We have set a chromecast here.")
            uris = device['uri'].split(":")
            host = uris[0]
            port = uris[1]
            Log.Debug("Host and port are %s and %s", host, port)
            cc = pychromecast.Chromecast(host, int(port))
            Log.Debug("Waiting for device")
            cc.wait(2)
            Log.Debug("Device is here!")
            if cc.is_idle != True:
                Log.Debug("We have a non-idle cast")
                status = "Running" + cc.app_display_name()
            else:
                status = "Idle"

            do = DirectoryObject(
                title=device['name'],
                duration=device['status'],
                tagline=device['uri'],
                summary=device['app']
            )
            oc.add(do)

    return oc


def fetch_devices(rescan=False):
    has_devices = Data.Exists('device_json')
    if has_devices == False:
        Log.Debug("No cached data exists, re-scanning.")
        casts = scan_devices()

    else:
        Log.Debug("Returning cached data")
        casts_string = Data.Load('device_json')
        casts = JSON.ObjectFromString(casts_string)

    port = os.environ.get("PLEXSERVERPORT")
    myurl = 'http://127.0.0.1:%s/clients' % port
    Log.Debug("Gonna connect to %s" % myurl)
    req = HTTP.Request(myurl)
    req.load()
    clientData = req.content
    root = ET.fromstring(clientData)
    for device in root.iter('Server'):
        local_item = {
            "name": device.get('name'),
            "uri": device.get('host') + ":" + str(device.get('port')),
            "status": "n/a",
            "type": device.get('product'),
            "app": "Plex Client",
            "id": device.get('machineIdentifier')
        }
        casts.append(local_item)

    return casts


# Scan our devices and save them to cache.
# This should NEVER be called from an endpoint...we don't have the time

def scan_devices():
    Log.Debug("Re-fetching devices")
    start_time = time.time()
    casts = pychromecast.get_chromecasts(1, None, None, True)
    Log.Debug("Save devices fired!")
    data_array = []
    for cast in casts:
        cast_item = {
            "uri": cast.uri,
            "name": cast.name,
            "status": cast.is_idle,
            "type": cast.cast_type,
            "app": cast.app_display_name,
            'id': cast.uri
        }
        data_array.append(cast_item)

    Log.Debug("Item count is " + str(len(data_array)))

    Log.Debug("Item count is " + str(len(data_array)))
    cast_string = JSON.StringFromObject(data_array)
    Data.Save('device_json', cast_string)
    last_scan = "Last Scan: " + time.strftime("%B %d %Y - %H:%M")
    Data.Save('last_scan', last_scan)


def getTimeDifferenceFromNow(TimeStart, TimeEnd):
    timeDiff = TimeEnd - TimeStart
    return timeDiff.total_seconds() / 60


def sort_headers(list, strict=False):
    returns = {}
    for key, value in Request.Headers.items():
        Log.Debug("Header key %s is %s", key, value)
        for item in list:
            if key in ("X-Plex-" + item, item):
                Log.Debug("We have a " + item)
                returns[item] = unicode(value)
                list.remove(item)

    if strict == True:
        len2 = len(list)
        if len2 == 0:
            Log.Debug("We have all of our values: " + JSON.StringFromObject(returns))
            return returns

        else:
            Log.Error("Sorry, parameters are missing.")
            for item in list:
                Log.Error("Missing " + item)
            return False
    else:
        return returns


def player_string(values):
    request_id = values['Requestid']
    content_id = values['Contentid'] + '?own=1&window=200'  # key
    content_type = values['Contenttype']
    offset = values['Offset']
    server_id = values['Serverid']
    transcoder_video = values['Transcodervideo']
    # TODO: Make this sexy, see if we can just use the current server. I think so.
    server_uri = values['Serveruri'].split("://")
    server_parts = server_uri[1].split(":")
    server_protocol = server_uri[0]
    server_ip = server_parts[0]
    server_port = server_parts[1]
    # TODO: Look this up instead of send it?
    username = values['Username']
    true = "true"
    false = "false"
    requestArray = {
        "type": 'LOAD',
        'requestId': request_id,
        'media': {
            'contentId': content_id,
            'streamType': 'BUFFERED',
            'contentType': content_type,
            'customData': {
                'offset': offset,
                'directPlay': true,
                'directStream': true,
                'subtitleSize': 100,
                'audioBoost': 100,
                'server': {
                    'machineIdentifier': server_id,
                    'transcoderVideo': transcoder_video,
                    'transcoderVideoRemuxOnly': false,
                    'transcoderAudio': true,
                    'version': '1.4.3.3433',
                    'myPlexSubscription': true,
                    'isVerifiedHostname': true,
                    'protocol': server_protocol,
                    'address': server_ip,
                    'port': server_port,
                    'user': {
                        'username': username
                    }
                },
                'containerKey': content_id
            },
            'autoplay': true,
            'currentTime': 0
        }
    }
    Log.Debug("Player String: " + JSON.StringFromObject(requestArray))

    return requestArray


def get_log_paths():
    # find log handler
    server_log_path = False
    plugin_log_path = False
    for handler in Core.log.handlers:
        if getattr(getattr(handler, "__class__"), "__name__") in (
                'FileHandler', 'RotatingFileHandler', 'TimedRotatingFileHandler'):
            plugin_log_file = handler.baseFilename
            if os.path.isfile(os.path.realpath(plugin_log_file)):
                plugin_log_path = plugin_log_file
                Log.Debug("Found a plugin path: " + plugin_log_path)

            if plugin_log_file:
                server_log_file = os.path.realpath(os.path.join(plugin_log_file, "../../Plex Media Server.log"))
                if os.path.isfile(server_log_file):
                    server_log_path = server_log_file
                    Log.Debug("Found a server log path: " + server_log_path)

    return [plugin_log_path, server_log_path]
