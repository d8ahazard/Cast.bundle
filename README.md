# Cast.bundle

Control chromecast devices through Plex.

## Installation:

Either download this file as a zip, and extract the directory Cast.bundle to your
Plex plug-in directory, or if you have WebTools installed, enter the following url 
to automatically install the plugin.

https://github.com/d8ahazard/Cast.bundle

## Usage:

There are a number of endpoints available for playback control.

Each is a GET endpoint, and requires specific headers for proper playback.

All endpoints are specified as follows:

http://your.server.address:32400/chromecast/

ALL queries require the ?X-Plex-Token= as part of the query string or header.

## Headers:

Headers can be specified as a normal header via GET, or appended to the query string by adding
'X-Plex-' to the query parameter. For 'path', you would add &X-Plex-path=somePath to the query.


## /Devices

Returns a standard Plex-formatted Mediacontainer, populated with a list of 
cast devices as <Device> nodes in the primary mediacontainer.

Device data is retrieved from cache and re-scanned every 10 minutes.

Does not require any other headers.

## /Rescan

Rescans all devices and stores their information into cache, then returns the 
same data as found from the /Devices endpoint.

TODO:
## /Play

Plays media from a Plex Media server. Requires a bunch of headers that I have to look up.

TODO:
## /Cmd

Issues a media control command. Need to grab a list of the proper formatting.

Required headers are "cmd" and "uri", where "cmd" is the command, and "uri" is the uri 
of the cast device to control.

Should add an option for friendlyName as well.

## /Broadcast

Broadcast an audio clip to all audio cast devices in cache.

Required headers: "path", where "path" is a publicly accessible URL to MP3-encoded audio.

TODO: Add optional audio type for non-mp3.

## /Audio

Plays an audio clip to the specified cast device.

Required headers: "path", "uri"

## /Status

Fetches the current status of the specified device

Required headers: "uri"

TODO: Make this return all device statuses if no URI specified.
For completeness, this should probably be like /Devices/URI/Status or
just the result of /Devices/URI or /Devices/Friendlyname
