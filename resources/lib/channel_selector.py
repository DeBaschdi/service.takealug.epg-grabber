
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import json
import os


ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")

# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)

# Make OSD Notify Messages
OSD = xbmcgui.Dialog()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

def select_channels(provider,chlist_provider,chlist_selected):
    dialog = xbmcgui.Dialog()
    ret = dialog.multiselect('Select Channels for Provider ' + provider, ["Foo", "Bar", "Baz"], preselect=[1, 2])
    print ret
    #log('Selected' + ret, xbmc.LOGNOTICE)

    xbmcvfs.copy(chlist_provider,chlist_selected)