# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

import os
from resources.lib import xml_structure
from resources.providers import magenta_DE
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")

## Read Global Settings
storage_path = ADDON.getSetting('storage_path').encode('utf-8')

## Get Enabled Grabbers
enable_grabber_magenta = True if ADDON.getSetting('enable_grabber_magenta').upper() == 'TRUE' else False

guide_temp = os.path.join(temppath, 'guide.xml')
guide_dest = os.path.join(storage_path, 'guide.xml')

# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)

# Make OSD Notify Messages
OSD = xbmcgui.Dialog()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

def grab_magenta_DE():
    if enable_grabber_magenta == True:
        magenta_DE.startup()

def check_startup():
    #Create Tempfile if not exist
    if not os.path.exists(temppath):
        os.makedirs(temppath)
    if storage_path == 'choose':
        notify(addon_name, 'You need to setup an Storage Path first', icon=xbmcgui.NOTIFICATION_ERROR)

    #Check if any Grabber is enabled
    enabled_grabber = True if ADDON.getSetting('enable_grabber_magenta').upper() == 'TRUE' else False

    if enabled_grabber == False:
        notify(addon_name, 'You need to enable at least 1 Grabber In Provider Settings', icon=xbmcgui.NOTIFICATION_WARNING)
        xbmc.sleep(2000)
        exit()

def copy_guide_to_destination():
    done = xbmcvfs.copy(guide_temp, guide_dest)
    if done == True:
        xbmc.sleep(5000)
        notify(addon_name, 'EPG File (guide.xml) Created', icon=xbmcgui.NOTIFICATION_INFO)

def startup():
    check_startup()
    xml_structure.xml_start()
    grab_magenta_DE()
    xml_structure.xml_end()
    copy_guide_to_destination()

startup()
