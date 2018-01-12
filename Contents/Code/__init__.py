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
    ObjectContainer.title1 = NAME  + VERSION
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = 0


@handler(PREFIX, NAME, thumb=ICON)
@route(PREFIX + '/MainMenu')
def MainMenu(random=0):
    """
    Main menu
    """
    Log.Debug("**********  Starting MainMenu  **********")    
    title = NAME  + VERSION
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
    Log.Debug('Reciever a call for Function 1')
    title = 'You called func 1'

    # Create a dummy container to return, in order to make
    # the framework happy
    oc = ObjectContainer(
        title1=title,
        no_cache=True,
        no_history=True)
    return oc


@route(PREFIX + '/Func2')
def Func2():
    """
    This is the first function to call
    """
    print 'Ged Func2'
    Log.Debug('Reciever a call for Function 2')
    title = 'You called Func 2'
    oc = ObjectContainer(
        title1=title,
        no_cache=True,
        no_history=True)
    return oc
