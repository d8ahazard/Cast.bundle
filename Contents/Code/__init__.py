############################################################################
# This plugin will create a list of medias in a section of Plex as a csv file,
# or as an xlsx file
#
# Made by
# dane22....A Plex Community member
#
############################################################################

# To find Work in progress, search this file for the word
# ToDo in all the modules
import json

# Constanst used
NAME = 'FlexTV.bundle'
VERSION = '1.0.0'
PREFIX = '/applications/FlexTV'
ICON = 'icon-default.png'


# Start function
def Start():
    print 'Ged 44 starting'
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


@route(PREFIX + '/Func1')
def Func1():
    """
    This is the first function to call
    """
    Log.Debug('Recieved a call for Function 1')
    param = unicode(Request.Headers[NAME])
    Log.Debug('Params are %s' % param)
    title = 'You called func 1 with the following headers: %s' % param
    # Create a dummy container to return, in order to make
    # the framework happy.
    # Can be used if needed to get a return value, by replacing
    # title with what you want to return
    oc = ObjectContainer(
        title1=title,
        no_cache=True,
        no_history=True)
    return oc


@route(PREFIX + '/Func2')
def Func2():
    """
    This is the second function to call
    """
    Log.Debug('Recieved a call for Function 2')
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
