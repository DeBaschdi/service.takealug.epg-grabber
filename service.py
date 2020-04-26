# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import time
from datetime import datetime
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
auto_download = True if ADDON.getSetting('auto_download').lower() == 'true' else False
timeswitch = int(ADDON.getSetting('timeswitch'))
timeoffset = (int(ADDON.getSetting('timeoffset')) * 12 + 24) * 3600

## Get Enabled Grabbers
enable_grabber_magenta = True if ADDON.getSetting('enable_grabber_magenta').upper() == 'TRUE' else False

# Check if any Grabber is enabled
enabled_grabber = True if ADDON.getSetting('enable_grabber_magenta').upper() == 'TRUE' else False

guide_temp = os.path.join(temppath, 'guide.xml')
guide_dest = os.path.join(storage_path, 'guide.xml')

## deal with setting 'last_download/next_download' which not exists at first time
try:
    next_download = int(ADDON.getSetting('next_download'))
except ValueError:
    ADDON.setSetting('next_download', str(int(time.time())))
try:
    last_download = int(ADDON.getSetting('last_download'))
except ValueError:
    ADDON.setSetting('last_download', str(int(time.time())))

## Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)

## Make OSD Notify Messages
OSD = xbmcgui.Dialog()

## MAKE an Monitor
Monitor = xbmc.Monitor()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

def grab_magenta_DE():
    if enable_grabber_magenta == True:
        magenta_DE.startup()

def copy_guide_to_destination():
    done = xbmcvfs.copy(guide_temp, guide_dest)
    if done == True:
        ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
        xbmc.sleep(5000)
        notify(addon_name, 'EPG File (guide.xml) Created', icon=xbmcgui.NOTIFICATION_INFO)
        ADDON.setSetting('last_download', str(int(time.time())))
        log('EPG File (guide.xml) Created', xbmc.LOGNOTICE)
    else:
        notify(addon_name, 'Can not copy guide.xml to Destination', icon=xbmcgui.NOTIFICATION_ERROR)
        log('Can not copy guide.xml to Destination', xbmc.LOGERROR)

def run_grabber():
    check_startup()
    xml_structure.xml_start()
    grab_magenta_DE()
    xml_structure.xml_end()
    copy_guide_to_destination()


def worker(next_download):
    dl_attempts = 0
    while not Monitor.waitForAbort(60):
        ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
        log('Worker walk through...')
        initiate_download = False

        # check if property 'last_download' in settings already exists and check timestamp of this file.
        # if timestamp is not older than 24 hours, there's nothing to do, otherwise download GZIP.

        try:
            last_timestamp = int(ADDON.getSetting('last_download'))
        except ValueError:
            last_timestamp = 0

        if last_timestamp > 0:
            log('Timestamp of last generated guide.xml is %s' % datetime.fromtimestamp(last_timestamp).strftime(
                '%d.%m.%Y %H:%M'), xbmc.LOGNOTICE)
            if (int(time.time()) - timeoffset) < last_timestamp < int(time.time()):
                log('Waiting for next EPG grab at %s' % datetime.fromtimestamp(next_download).strftime(
                    '%d.%m.%Y %H:%M'), xbmc.LOGNOTICE)
            else:
                log('guide.xml is older than %s hours, initiate EPG grab' % (timeoffset / 86400))
                initiate_download = True

            if next_download < int(time.time()):
                # suggested download time has passed (e.g. system was offline) or time is now, download epg
                # and set a new timestamp for the next download
                log('Download time has reached, initiate download', xbmc.LOGNOTICE)
                initiate_download = True
        else:
            initiate_download = True

        if initiate_download:
            if dl_attempts < 3:
                notify(addon_name, 'Initialize Auto EPG Grab...', icon=xbmcgui.NOTIFICATION_INFO)
                if run_grabber():
                    dl_attempts = 0
                    #xbmcvfs.delete(cookie)
                else:
                    dl_attempts += 1
            else:
                # has tried 3x to download files in a row, giving up
                ADDON.setSetting('last_download', str(int(time.time())))
                log("Tried downlad 3x without success", xbmc.LOGERROR)

            calc_next_download = datetime.now()
            calc_next_download = calc_next_download.replace(day=calc_next_download.day + 1, hour=timeswitch, minute=0,
                                                            second=0, microsecond=0)

            # Deal with a windows strftime bug (Win don't know '%s' formatting)
            try:
                next_download = int(calc_next_download.strftime("%s"))
            except ValueError:
                next_download = int(time.mktime(calc_next_download.timetuple()))

            ADDON.setSetting('next_download', str(next_download))


def check_startup():
    #Create Tempfolder if not exist
    if not os.path.exists(temppath):
        os.makedirs(temppath)
    if storage_path == 'choose':
        notify(addon_name, 'You need to setup an Storage Path first', icon=xbmcgui.NOTIFICATION_ERROR)
        return False

    if enabled_grabber == False:
        notify(addon_name, 'You need to enable at least 1 Grabber In Provider Settings', icon=xbmcgui.NOTIFICATION_ERROR)
        xbmc.sleep(2000)
        return False
    ## Clean Tempfiles
    for file in os.listdir(temppath): xbmcvfs.delete(os.path.join(temppath, file))
    return True


# Addon starts at this point

if check_startup():
    try:
        if sys.argv[1] == 'manual_download':
            if storage_path == 'choose':
                notify(addon_name, 'You need to setup an Storage Path first', icon=xbmcgui.NOTIFICATION_ERROR)
            elif enabled_grabber == False:
                notify(addon_name, 'You need to enable at least 1 Grabber In Provider Settings', icon=xbmcgui.NOTIFICATION_ERROR)
            else:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno('Takealug EPG Grabber', 'Start grabbing EPG Data ?')
                if ret:
                    manual = True
                    notify(addon_name, 'Initialize Manual EPG Grab...', icon=xbmcgui.NOTIFICATION_INFO)
                    run_grabber()

    except IndexError:
        if auto_download:
            if storage_path == 'choose':
                notify(addon_name, 'You need to setup an Storage Path first', icon=xbmcgui.NOTIFICATION_ERROR)
            elif enabled_grabber == False:
                notify(addon_name, 'You need to enable at least 1 Grabber In Provider Settings', icon=xbmcgui.NOTIFICATION_ERROR)
            else:
                worker(int(ADDON.getSetting('next_download')))