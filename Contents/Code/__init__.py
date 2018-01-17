############################################################################
# This plugin will allow external calls, that the plugin can then handle
# See TODO doc for more details
#
# Made by
# dane22....A Plex Community member
#
############################################################################

# To find Work in progress, search this file for the word
# ToDo in all the modules
from __future__ import print_function

import pychromecast
import pychromecast.controllers.plex as plexCast
import time
import json



# Constanst used
NAME = 'FlexTV'
VERSION = '1.1.0'
PREFIX = '/applications/FlexTV'
ICON = 'icon-default.png'


# Start function
def Start():
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    ObjectContainer.title1 = NAME + VERSION
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = 0


@handler(PREFIX, NAME, thumb=ICON)
@route(PREFIX + '/MainMenu')
def MainMenu(random=0):
    """
    Main menu
    """
    Log.Debug("**********  Starting MainMenu  **********")
    title = NAME + VERSION
    #TODO: Build that list of cast devices and show them here?
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
    casts = pychromecast.get_chromecasts()
    count = len(casts)
    Log.Debug("Found " + str(count) + " cast devices!")
    if len(casts) == 0:
        Status = "No Devices Found"
    else:
        Status = "Devices found"
        # TODO: Take what's in casts and build device entries inside oc


    oc = ObjectContainer(
        title1="Cast Devices",
        title2=Status,
        no_cache=True,
        no_history=True)
    for cast in casts:
        oc.add(DirectoryObject(
            title=cast.name,
            duration=cast.is_idle,
            tagline=cast.app_id,
            summary=cast.cast_type,
            thumb=cast.uri
        ))


    return oc


@route(PREFIX + '/Play')
def Play():
    """
    Endpoint to play media. 
	
	Sends to "urn:x-cast:com.google.cast.media", with JSON,
	after verifying that the Plex app is running on cast device
	
	JSON Array Looks like this:
		[
			'type' => 'LOAD',
			'requestId' => $requestId,
			'media' => [
				'contentId' => (string)$key,
				'streamType' => 'BUFFERED',
				'contentType' => ($transcoderVideo ? 'video' : 'music'),
				'customData' => [
					'offset' => ($media['viewOffset'] ?? 0),
					'directPlay' => true,
					'directStream' => true,
					'subtitleSize' => 100,
					'audioBoost' => 100,
					'server' => [
						'machineIdentifier' => $machineIdentifier,
						'transcoderVideo' => $transcoderVideo,
						'transcoderVideoRemuxOnly' => false,
						'transcoderAudio' => true,
						'version' => '1.4.3.3433',
						'myPlexSubscription' => true,
						'isVerifiedHostname' => true,
						'protocol' => $serverProtocol,
						'address' => $serverIP,
						'port' => $serverPort,
						'accessToken' => $transientToken,
						'user' => [
							'username' => $userName
						],
						'containerKey' => $queueID . '?own=1&window=200'
					],
					'autoplay' => true,
					'currentTime' => 0
				]
			]
		]
		
		Needed params in request headers:
		Cast device IP:PORT
		Request ID - FlexTV Command ID
		Content ID
		Content Type ('video'/'music')
		Start Offset
		Server ID
		TranscoderVideo - Does it need to transcode video?
		Server Protocol, address, port, transient token
		Username
		ContainerKey
	
    """
    Log.Debug('Recieved a call to play media.')
    param = unicode(Request.Headers[NAME])
    Log.Debug('Params are %s' % param)
    title = 'You called func 1 with the following headers: %s' % param
    # Create a dummy container to return, in order to make
    # the framework happy
    # Can be used if needed to get a return value, by replacing title var with
    # what you want to return
    oc = ObjectContainer(
        title1=title,
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

	
	Additionally, volume commands can be issued using:
	
	Mute:
	"urn:x-cast:com.google.cast.receiver", '{"type":"SET_VOLUME", "volume": { "muted": true }, "requestId":1 }'
	
	Unmute:
	"urn:x-cast:com.google.cast.receiver", '{"type":"SET_VOLUME", "volume": { "muted": false }, "requestId":1 }'
	
	Volume (Where $volume is an int from 0-100):
	"urn:x-cast:com.google.cast.receiver", '{"type":"SET_VOLUME", "volume": { "level": ' . $volume . ' }, "requestId":1 }'
	
    """
    Log.Debug('Recieved a call to control playback')
    chromecasts = pychromecast.get_chromecasts()
    client = unicode(Request.Headers["client"])
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == client)
    command = unicode(Request.Headers["command"])
    Log.Debug('Params are %s' % client % ' and ' % command)
    if (len(cast) != 0):
        cast.wait()
        if (command == "VOLUME"):
            level = unicode(Request.Headers["level"])
            Log.Debug('Trying to set volume to ' % level)
            mc = cast.media_controller
            # TODO: Send the volume command, dude.
        if ((command == "MUTE") | (command == "UNMUTE")):
            mc = cast.media_controller
            # TODO: Mute/unmute
        else:
            d = plexCast.PlexController()
            cast.register_handler(d)
            message = PlexFunction(command)
            Log.Debug('Formatted Plex message is ' % message)
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
    if (len(cast) != 0):
        #TODO: Convert status to json or something?
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