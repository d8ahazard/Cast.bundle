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
import time
import pychromecast
import json

# Constanst used
NAME = 'FlexTV'
VERSION = '1.0.1'
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
	Will need to call pyChromeCast's method to fetch devices, return as an array of JSON
    """
    Log.Debug('Recieved a call to fetch devices')
    param = unicode(Request.Headers[NAME])
    Log.Debug('Params are %s' % param)
    title = 'You called func 1 with the following headers: %s' % param
    # Create a dummy container to return, in order to make
    # the framework happy.
    # Can be used if needed to get a return value, by replacing
    # title with what you want to return
    oc = ObjectContainer(
        title1="Trythisagain",
		title2='singleQuotes',
        no_cache=True,
        no_history=True)
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
	
	"urn:x-cast:plex", '{"type":"<COMMAND>"}'
	
	Where <COMMAND> is one of:
	PLAY (resume)
	PAUSE
	STOP
	STEPFORWARD
	STEPBACK (BACKWARD? Need to test, not in PHP cast app)
	PREVIOUS
	NEXT
	
	Additionally, volume commands can be issued using:
	
	Mute:
	"urn:x-cast:com.google.cast.receiver", '{"type":"SET_VOLUME", "volume": { "muted": true }, "requestId":1 }'
	
	Unmute:
	"urn:x-cast:com.google.cast.receiver", '{"type":"SET_VOLUME", "volume": { "muted": false }, "requestId":1 }'
	
	Volume (Where $volume is an int from 0-100):
	"urn:x-cast:com.google.cast.receiver", '{"type":"SET_VOLUME", "volume": { "level": ' . $volume . ' }, "requestId":1 }'
	
    """
    Log.Debug('Recieved a call to control playback')
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
	
	
@route(PREFIX + '/Status')
def Status():
    """
    Fetch player status
	"urn:x-cast:com.google.cast.media", '{"type":"GET_STATUS", "requestId":1}'
	
	Then filter for "/{\"type.*/"
	
    """
    Log.Debug('Recieved a call to control playback')
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
	
def LaunchApp():
	"""
	Internal method needed to launch/verify Plex app is loaded
	on cast device before sending other commands.
	
	Should return true/false boolean before other commands.
	
	Plex Cast application ID is "9AC194DC"
	"""
