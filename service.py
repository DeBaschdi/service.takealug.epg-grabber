# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import time
from datetime import datetime
from datetime import timedelta
import os
import json
import re
from collections import Counter
from resources.lib import xml_structure
from resources.providers import magenta_DE
from resources.providers import horizon_DE
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
loc = ADDON.getLocalizedString
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")

## Read Global Settings
storage_path = ADDON.getSetting('storage_path').encode('utf-8')
auto_download = True if ADDON.getSetting('auto_download').lower() == 'true' else False
timeswitch = int(ADDON.getSetting('timeswitch'))
timeoffset = (int(ADDON.getSetting('timeoffset')) * 12 + 24) * 3600
enable_rating_mapper = True if ADDON.getSetting('enable_rating_mapper').upper() == 'TRUE' else False

## Get Enabled Grabbers
enable_grabber_magentaDE = True if ADDON.getSetting('enable_grabber_magentaDE').upper() == 'TRUE' else False
enable_grabber_hznDE = True if ADDON.getSetting('enable_grabber_hznDE').upper() == 'TRUE' else False

# Check if any Grabber is enabled
if (enable_grabber_magentaDE or enable_grabber_hznDE):
    enabled_grabber = True
else:
    enabled_grabber = False

guide_temp = os.path.join(temppath, 'guide.xml')
guide_dest = os.path.join(storage_path, 'guide.xml')
grabber_cron = os.path.join(datapath, 'grabber_cron.json')
grabber_cron_tmp = os.path.join(temppath, 'grabber_cron.json')

## Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)

## Make OSD Notify Messages
OSD = xbmcgui.Dialog()

## MAKE an Monitor
Monitor = xbmc.Monitor()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

def copy_guide_to_destination():
    done = xbmcvfs.copy(guide_temp, guide_dest)
    if done == True:
        xbmc.sleep(3000)
        notify(addon_name, loc(32350), icon=xbmcgui.NOTIFICATION_INFO)
        log(loc(32350), xbmc.LOGNOTICE)

        ## Write new setting last_download
        with open(grabber_cron, 'r') as f:
            data = json.load(f)
            data['last_download'] = str(int(time.time()))

        with open(grabber_cron_tmp, 'w') as f:
            json.dump(data, f, indent=4)
        ## rename temporary file replacing old file
        xbmcvfs.copy(grabber_cron_tmp, grabber_cron)
        xbmcvfs.delete(grabber_cron_tmp)
        f.close()

    else:
        notify(addon_name, loc(32351), icon=xbmcgui.NOTIFICATION_ERROR)
        log(loc(32351), xbmc.LOGERROR)

def check_channel_dupes():
    with open(guide_temp) as f:
        c = Counter(c.strip().lower() for c in f if c.strip())  # for case-insensitive search
        dupe = []
        for line in c:
            if c[line] > 1:
                if ('display-name' in line or 'icon src' in line or '</channel' in line):
                    pass
                else:
                    dupe.append(line + '\n')
        dupes = ''.join(dupe)

        if (not dupes == ''):
            log('{} {}'.format(loc(32400),line), xbmc.LOGERROR)
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('-]ERROR[- {}'.format(loc(32400)), dupes)
            if ok:
                exit()

def run_grabber():
    check_startup()
    xml_structure.xml_start()
    ## Check Provider
    if enable_grabber_magentaDE == True:
        magenta_DE.startup()
    if enable_grabber_hznDE == True:
        horizon_DE.startup()

    ## Create XML Channels
    if enable_grabber_magentaDE == True:
        magenta_DE.create_xml_channels()
    if enable_grabber_hznDE == True:
        horizon_DE.create_xml_channels()

    # Check for Channel Dupes
    check_channel_dupes()

    ## Create XML Broadcast
    if enable_grabber_magentaDE == True:
        magenta_DE.create_xml_broadcast(enable_rating_mapper)
    if enable_grabber_hznDE == True:
        horizon_DE.create_xml_broadcast(enable_rating_mapper)

    ## Finish XML
    xml_structure.xml_end()
    copy_guide_to_destination()


def worker():
    dl_attempts = 0
    while not Monitor.waitForAbort(60):
        with open(grabber_cron, 'r') as j:
            cron = json.load(j)
            next_download = int(cron['next_download'])
        j.close()
        initiate_download = False

        # check if property 'last_download' in settings already exists and check timestamp of this file.
        # if timestamp is not older than 24 hours, there's nothing to do, otherwise grab EPG.

        try:
            with open(grabber_cron, 'r') as j:
                cron = json.load(j)
                last_timestamp = int(cron['last_download'])
            j.close()
        except ValueError:
            last_timestamp = 0

        if last_timestamp > 0:
            log('{} {}'.format(loc(32352),datetime.fromtimestamp(last_timestamp).strftime('%d.%m.%Y %H:%M')), xbmc.LOGNOTICE)
            if (int(time.time()) - timeoffset) < last_timestamp < int(time.time()):
                log('{} {}'.format(loc(32353),datetime.fromtimestamp(next_download).strftime('%d.%m.%Y %H:%M')), xbmc.LOGNOTICE)
            else:
                log('{} {} {}'.format(loc(32354),(timeoffset / 86400),loc(32355)), xbmc.LOGNOTICE)
                initiate_download = True

            if next_download < int(time.time()):
                # suggested download time has passed (e.g. system was offline) or time is now, download epg
                # and set a new timestamp for the next download
                log(loc(32356), xbmc.LOGNOTICE)
                initiate_download = True
        else:
            initiate_download = True

        if initiate_download:
            if dl_attempts < 3:
                notify(addon_name, loc(32357), icon=xbmcgui.NOTIFICATION_INFO)
                if run_grabber():
                    dl_attempts = 0
                else:
                    dl_attempts += 1
            else:
                # has tried 3x to download files in a row, giving up
                ## Write new setting last_download
                with open(grabber_cron, 'r') as f:
                    data = json.load(f)
                    data['last_download'] = str(int(time.time()))

                with open(grabber_cron_tmp, 'w') as f:
                    json.dump(data, f, indent=4)
                ## rename temporary file replacing old file
                xbmcvfs.copy(grabber_cron_tmp, grabber_cron)
                xbmcvfs.delete(grabber_cron_tmp)
                f.close()
                log(loc(32358), xbmc.LOGERROR)

        # Calculate Next_Download Setting
        calc_next_download = datetime.now()
        calc_next_download = calc_next_download.replace(day=calc_next_download.day , hour=timeswitch, minute=0, second=0, microsecond=0)
        calc_next_download += timedelta(days=1)

        # Deal with a windows strftime bug (Win don't know '%s' formatting)
        try:
            next_download = int(calc_next_download.strftime("%s"))
        except ValueError:
            next_download = int(time.mktime(calc_next_download.timetuple()))

        ## Write new setting next_download
        with open(grabber_cron, 'r') as f:
            data = json.load(f)
            data['next_download'] = str(next_download)
            tempfile = os.path.join(temppath, 'filename')

        with open(tempfile, 'w') as f:
            json.dump(data, f, indent=4)
        ## rename temporary file replacing old file
        xbmcvfs.copy(tempfile, grabber_cron)
        xbmcvfs.delete(tempfile)
        f.close()


def check_startup():
    #Create Tempfolder if not exist
    if not os.path.exists(temppath):
        os.makedirs(temppath)
    if storage_path == 'choose':
        notify(addon_name, loc(32359), icon=xbmcgui.NOTIFICATION_ERROR)
        return False

    if enabled_grabber == False:
        notify(addon_name, loc(32360), icon=xbmcgui.NOTIFICATION_ERROR)
        xbmc.sleep(2000)
        return False

    ## deal with setting 'last_download/next_download' which not exists at first time
    if (not os.path.isfile(grabber_cron)):
        with open(grabber_cron, 'w') as downloads:
            downloads.write(json.dumps({}))
            downloads.close()

    # Calculate Next_Download Setting
    calc_next_download = datetime.now()
    calc_next_download = calc_next_download.replace(day=calc_next_download.day , hour=timeswitch, minute=0, second=0, microsecond=0)
    calc_next_download += timedelta(days=1)

    # Deal with a windows strftime bug (Win don't know '%s' formatting)
    try:
        next_download = int(calc_next_download.strftime("%s"))
    except ValueError:
        next_download = int(time.mktime(calc_next_download.timetuple()))

    with open(grabber_cron, 'r') as f:
        data = json.load(f)
        if 'last_download' not in data:
            data['last_download'] = str(int(time.time()))
            log('creating setting last_download')
        if 'next_download' not in data:
            data['next_download'] = next_download
        tempfile = os.path.join(temppath, 'filename')
        with open(tempfile, 'w') as f:
            json.dump(data, f, indent=4)
        ## rename temporary file replacing old file
        xbmcvfs.copy(tempfile, grabber_cron)
        xbmcvfs.delete(tempfile)
        f.close()

    ## Clean Tempfiles
    for file in os.listdir(temppath): xbmcvfs.delete(os.path.join(temppath, file))
    return True


# Addon starts at this point

if check_startup():
    try:
        if sys.argv[1] == 'manual_download':
            if storage_path == 'choose':
                notify(addon_name, loc(32359), icon=xbmcgui.NOTIFICATION_ERROR)
            elif enabled_grabber == False:
                notify(addon_name, loc(32360), icon=xbmcgui.NOTIFICATION_ERROR)
            else:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno('Takealug EPG Grabber', loc(32401))
                if ret:
                    manual = True
                    notify(addon_name, loc(32357), icon=xbmcgui.NOTIFICATION_INFO)
                    run_grabber()

    except IndexError:
        if auto_download:
            if storage_path == 'choose':
                notify(addon_name, loc(32359), icon=xbmcgui.NOTIFICATION_ERROR)
            elif enabled_grabber == False:
                notify(addon_name, loc(32360), icon=xbmcgui.NOTIFICATION_ERROR)
            else:
                worker()