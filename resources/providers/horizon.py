# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import json
import os
import sys
import requests.cookies
import requests
import requests.adapters
import time
from datetime import timedelta
from datetime import datetime
from resources.lib import xml_structure
from resources.lib import channel_selector
from resources.lib import mapper
from resources.lib import filesplit


def get_hzndict(grabber):
    ## 0=provider, 1=lang, 2=temppath, 3=genre_warnings, 4=channel_warnings, 5=days_to_grab, 6=episode_format, 7=channel_format, 8=genre_format, 9=chlist_provider_tmp, 10=chlist_provider, 11=chlist_selected, 12=url
    hzndict = dict({'de': ['HORIZON (DE)', 'de', 'horizonDE', 'hznDE_genres_warnings.txt', 'hznDE_channels_warnings.txt', 'hznDE_days_to_grab', 'hznDE_episode_format', 'hznDE_channel_format' ,'hznDE_genre_format', 'chlist_hznDE_provider_tmp.json', 'chlist_hznDE_provider.json', 'chlist_hznDE_selected.json', 'DE/deu'],
                    'at': ['HORIZON (AT)', 'at', 'horizonAT', 'hznAT_genres_warnings.txt', 'hznAT_channels_warnings.txt', 'hznAT_days_to_grab', 'hznAT_episode_format', 'hznAT_channel_format' ,'hznAT_genre_format', 'chlist_hznAT_provider_tmp.json', 'chlist_hznAT_provider.json', 'chlist_hznAT_selected.json', 'AT/deu'],
                    'ch': ['HORIZON (CH)', 'ch', 'horizonCH', 'hznCH_genres_warnings.txt', 'hznCH_channels_warnings.txt', 'hznCH_days_to_grab', 'hznCH_episode_format', 'hznCH_channel_format' ,'hznCH_genre_format', 'chlist_hznCH_provider_tmp.json', 'chlist_hznCH_provider.json', 'chlist_hznCH_selected.json', 'CH/deu'],
                    'nl': ['HORIZON (NL)', 'nl', 'horizonNL', 'hznNL_genres_warnings.txt', 'hznNL_channels_warnings.txt', 'hznNL_days_to_grab', 'hznNL_episode_format', 'hznNL_channel_format' ,'hznNL_genre_format', 'chlist_hznNL_provider_tmp.json', 'chlist_hznNL_provider.json', 'chlist_hznNL_selected.json', 'NL/nld'],
                    'pl': ['HORIZON (PL)', 'pl', 'horizonPL', 'hznPL_genres_warnings.txt', 'hznPL_channels_warnings.txt', 'hznPL_days_to_grab', 'hznPL_episode_format', 'hznPL_channel_format' ,'hznPL_genre_format', 'chlist_hznPL_provider_tmp.json', 'chlist_hznPL_provider.json', 'chlist_hznPL_selected.json', 'PL/pol'],
                    'ie': ['HORIZON (IE)', 'ie', 'horizonIE', 'hznIE_genres_warnings.txt', 'hznIE_channels_warnings.txt', 'hznIE_days_to_grab', 'hznIE_episode_format', 'hznIE_channel_format' ,'hznIE_genre_format', 'chlist_hznIE_provider_tmp.json', 'chlist_hznIE_provider.json', 'chlist_hznIE_selected.json', 'IE/eng'],
                    'gb': ['HORIZON (GB)', 'gb', 'horizonGB', 'hznGB_genres_warnings.txt', 'hznGB_channels_warnings.txt', 'hznGB_days_to_grab', 'hznGB_episode_format', 'hznGB_channel_format', 'hznGB_genre_format', 'chlist_hznGB_provider_tmp.json', 'chlist_hznGB_provider.json', 'chlist_hznGB_selected.json', 'GB/eng'],
                    'sk': ['HORIZON (SK)', 'sk', 'horizonSK', 'hznSK_genres_warnings.txt', 'hznSK_channels_warnings.txt', 'hznSK_days_to_grab', 'hznSK_episode_format', 'hznSK_channel_format' ,'hznSK_genre_format', 'chlist_hznSK_provider_tmp.json', 'chlist_hznSK_provider.json', 'chlist_hznSK_selected.json', 'SK/slk'],
                    'cz': ['HORIZON (CZ)', 'cz', 'horizonCZ', 'hznCZ_genres_warnings.txt', 'hznCZ_channels_warnings.txt', 'hznCZ_days_to_grab', 'hznCZ_episode_format', 'hznCZ_channel_format' ,'hznCZ_genre_format', 'chlist_hznCZ_provider_tmp.json', 'chlist_hznCZ_provider.json', 'chlist_hznCZ_selected.json', 'CZ/ces'],
                    'hu': ['HORIZON (HU)', 'hu', 'horizonHU', 'hznHU_genres_warnings.txt', 'hznHU_channels_warnings.txt', 'hznHU_days_to_grab', 'hznHU_episode_format', 'hznHU_channel_format' ,'hznHU_genre_format', 'chlist_hznHU_provider_tmp.json', 'chlist_hznHU_provider.json', 'chlist_hznHU_selected.json', 'HU/hun'],
                    'ro': ['HORIZON (RO)', 'ro', 'horizonRO', 'hznRO_genres_warnings.txt', 'hznRO_channels_warnings.txt', 'hznRO_days_to_grab', 'hznRO_episode_format', 'hznRO_channel_format' ,'hznRO_genre_format', 'chlist_hznRO_provider_tmp.json', 'chlist_hznRO_provider.json', 'chlist_hznRO_selected.json', 'RO/ron'],
                  })
    return hzndict

def get_settings(grabber):
    hzndict = get_hzndict(grabber)
    provider_temppath = os.path.join(temppath, hzndict[grabber][2])

    # EIT Genre + Rytec Format Mapping Files
    hzn_genres_json = os.path.join(provider_temppath, 'hzn_genres.json')
    hzn_channels_json = os.path.join(provider_temppath, 'hzn_channels.json')

    ## Log Files
    hzn_genres_warnings_tmp = os.path.join(provider_temppath, hzndict[grabber][3])
    hzn_genres_warnings = os.path.join(temppath, hzndict[grabber][3])
    hzn_channels_warnings_tmp = os.path.join(provider_temppath, hzndict[grabber][4])
    hzn_channels_warnings = os.path.join(temppath, hzndict[grabber][4])

    ## Read Horizon Settings
    days_to_grab = int(ADDON.getSetting(hzndict[grabber][5]))
    episode_format = ADDON.getSetting(hzndict[grabber][6])
    channel_format = ADDON.getSetting(hzndict[grabber][7])
    genre_format = ADDON.getSetting(hzndict[grabber][8])

    ## Channel Files
    hzn_chlist_provider_tmp = os.path.join(provider_temppath, hzndict[grabber][9])
    hzn_chlist_provider = os.path.join(provider_temppath, hzndict[grabber][10])
    hzn_chlist_selected = os.path.join(datapath, hzndict[grabber][11])

    provider = hzndict[grabber][0]
    lang = hzndict[grabber][1]

    return provider_temppath, hzn_genres_json, hzn_channels_json, hzn_genres_warnings_tmp, hzn_genres_warnings,hzn_channels_warnings_tmp, hzn_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, hzn_chlist_provider_tmp, hzn_chlist_provider, hzn_chlist_selected, provider, lang

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
loc = ADDON.getLocalizedString
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")

## Enable Multithread
enable_multithread = True if ADDON.getSetting('enable_multithread').upper() == 'TRUE' else False
if enable_multithread:
    try:
        from multiprocessing import Process
    except:
        pass

## MAPPING Variables Thx @ sunsettrack4
hzn_genres_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/hzn_genres.json'
hzn_channels_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/hzn_channels.json'

# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)


# Make OSD Notify Messages
OSD = xbmcgui.Dialog()


def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

def get_epgLength(days_to_grab):
    # Calculate Date and Time in Microsoft Timestamp
    today = datetime.today()
    calc_today = datetime(today.year, today.month, today.day, hour=00, minute=00, second=1)

    calc_then = datetime(today.year, today.month, today.day, hour=23, minute=59, second=59)
    calc_then += timedelta(days=days_to_grab)

    try:
        today = calc_today.strftime("%s")
        starttime = '{}000'.format(int(today))
    except ValueError:
        today = time.mktime(calc_today.timetuple())
        starttime = '{}000'.format(int(today))

    try:
        then = calc_then.strftime("%s")
        endtime = '{}000'.format(int(then))
    except ValueError:
        then = time.mktime(calc_then.timetuple())
        endtime = '{}000'.format(int(then))

    return starttime, endtime


hzn_header = {'Host': 'web-api-pepper.horizon.tv',
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
                  'Accept-Encoding': 'gzip',
                  'Connection': 'keep-alive',
                  'Upgrade-Insecure-Requests': '1'}

## Get channel list(url)
def get_channellist(grabber,hzndict,hzn_chlist_provider_tmp,hzn_chlist_provider):
    hzn_channellist_url = 'https://web-api-pepper.horizon.tv/oesp/v2/{}/web/channels'.format(hzndict[grabber][12])
    hzn_chlist_url = requests.get(hzn_channellist_url, headers=hzn_header)
    hzn_chlist_url.raise_for_status()
    response = hzn_chlist_url.json()
    with open(hzn_chlist_provider_tmp, 'w') as provider_list_tmp:
        json.dump(response, provider_list_tmp)

    #### Transform hzn_chlist_provider_tmp to Standard chlist Format as hzn_chlist_provider

    # Load Channellist from Provider
    with open(hzn_chlist_provider_tmp, 'r') as provider_list_tmp:
        hzn_channels = json.load(provider_list_tmp)

    # Create empty new hzn_chlist_provider
    with open(hzn_chlist_provider, 'w') as provider_list:
        provider_list.write(json.dumps({"channellist": []}))

    ch_title = ''

    # Load New Channellist from Provider
    with open(hzn_chlist_provider) as provider_list:
        data = json.load(provider_list)

        temp = data['channellist']

        for channels in hzn_channels['channels']:
            ch_id = channels['stationSchedules'][0]['station']['id']
            ch_title_dirty = channels['stationSchedules'][0]['station']['title']
            for image in channels['stationSchedules'][0]['station']['images']:
                try:
                    if image['assetType'] == 'station-logo-large':
                        hdimage_url = image['url'].split('?w')
                        hdimage = hdimage_url[0]
                except:
                    hdimage = ''
            ch_title = ch_title_dirty.replace(u'\u0086', '').replace(u'\u0087', '')
            # channel to be appended
            y = {"contentId": ch_id,
                 "name": ch_title,
                 "pictures": [{"href": hdimage}]}

            # appending channels to data['channellist']
            temp.append(y)

    #Save New Channellist from Provider
    with open(hzn_chlist_provider, 'w') as provider_list:
        json.dump(data, provider_list, indent=4)

def select_channels(grabber):
    provider_temppath, hzn_genres_json, hzn_channels_json, hzn_genres_warnings_tmp, hzn_genres_warnings, hzn_channels_warnings_tmp, hzn_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, hzn_chlist_provider_tmp, hzn_chlist_provider, hzn_chlist_selected, provider, lang = get_settings(grabber)
    hzndict = get_hzndict(grabber)
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(hzn_chlist_selected):
        with open(hzn_chlist_selected, 'w') as selected_list:
            selected_list.write(json.dumps({"channellist": []}))

    ## Download chlist_provider.json
    get_channellist(grabber,hzndict,hzn_chlist_provider_tmp,hzn_chlist_provider)
    dialog = xbmcgui.Dialog()

    with open(hzn_chlist_provider, 'r') as o:
        provider_list = json.load(o)

    with open(hzn_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    ## Start Channel Selector
    user_select = channel_selector.select_channels(provider, provider_list, selected_list)

    if user_select is not None:
        with open(hzn_chlist_selected, 'w') as f:
            json.dump(user_select, f, indent=4)
        if os.path.isfile(hzn_chlist_selected):
            valid = check_selected_list(hzn_chlist_selected)
            if valid is True:
                ok = dialog.ok(provider, loc(32402))
                if ok:
                    log(loc(32402), xbmc.LOGNOTICE)
            elif valid is False:
                log(loc(32403), xbmc.LOGNOTICE)
                yn = OSD.yesno(provider, loc(32403))
                if yn:
                    select_channels(grabber)
                else:
                    xbmcvfs.delete(hzn_chlist_selected)
                    exit()
    else:
        valid = check_selected_list(hzn_chlist_selected)
        if valid is True:
            ok = dialog.ok(provider, loc(32404))
            if ok:
                log(loc(32404), xbmc.LOGNOTICE)
        elif valid is False:
            log(loc(32403), xbmc.LOGNOTICE)
            yn = OSD.yesno(provider, loc(32403))
            if yn:
                select_channels(grabber)
            else:
                xbmcvfs.delete(hzn_chlist_selected)
                exit()

def check_selected_list(hzn_chlist_selected):
    check = 'invalid'
    with open(hzn_chlist_selected, 'r') as c:
        selected_list = json.load(c)
    for user_list in selected_list['channellist']:
        if 'contentId' in user_list:
            check = 'valid'
    if check == 'valid':
        return True
    else:
        return False

def download_multithread(thread_temppath, download_threads, grabber, hzn_chlist_selected, provider, provider_temppath, hzndict, days_to_grab):
    # delete old broadcast files if exist
    for f in os.listdir(provider_temppath):
        if f.endswith('_broadcast.json'):
            xbmcvfs.delete(os.path.join(provider_temppath, f))

    list = os.path.join(provider_temppath, 'list.txt')
    splitname = os.path.join(thread_temppath, 'chlist_hznXX_selected')
    starttime, endtime = get_epgLength(days_to_grab)

    with open(hzn_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    if filesplit.split_chlist_selected(thread_temppath, hzn_chlist_selected, splitname, download_threads, enable_multithread):
        multi = True
        needed_threads = sum([len(files) for r, d, files in os.walk(thread_temppath)])
        items_to_download = str(len(selected_list['channellist']))
        log('{} {} {} '.format(provider, items_to_download, loc(32361)), xbmc.LOGNOTICE)
        pDialog = xbmcgui.DialogProgressBG()
        log('{} Multithread({}) Mode'.format(provider, needed_threads), xbmc.LOGNOTICE)
        pDialog.create('{} {} '.format(loc(32500), provider), '{} {}'.format('100', loc(32501)))

        jobs = []
        for thread in range(0, int(needed_threads)):
            p = Process(target=download_thread, args=(grabber, '{}_{}.json'.format(splitname, int(thread)), multi, list, provider, provider_temppath, hzndict, days_to_grab, starttime, endtime, ))
            jobs.append(p)
            p.start()
        for j in jobs:
            while j.is_alive():
                xbmc.sleep(500)
                try:
                    last_line = ''
                    with open(list, 'r') as f:
                        last_line = f.readlines()[-1]
                except:
                    pass
                items = sum(1 for f in os.listdir(provider_temppath) if f.endswith('_broadcast.json'))
                percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
                percent_completed = int(100) * int(items) / int(items_to_download)
                pDialog.update(int(percent_completed), '{} {} '.format(loc(32500), last_line), '{} {} {}'.format(int(percent_remain), loc(32501), provider))
                if int(items) == int(items_to_download):
                    log('{} {}'.format(provider, loc(32363)), xbmc.LOGNOTICE)
                    break
            j.join()
        pDialog.close()
        for file in os.listdir(thread_temppath): xbmcvfs.delete(os.path.join(thread_temppath, file))
    else:
        multi = False
        download_thread(grabber, hzn_chlist_selected, multi, list, provider, provider_temppath, hzndict, days_to_grab, starttime, endtime)

def download_thread(grabber, hzn_chlist_selected, multi, list, provider, provider_temppath, hzndict, days_to_grab, starttime, endtime):
    requests.adapters.DEFAULT_RETRIES = 5

    with open(hzn_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    if not multi:
        items_to_download = str(len(selected_list['channellist']))
        log('{} {} {} '.format(provider, items_to_download, loc(32361)), xbmc.LOGNOTICE)
        pDialog = xbmcgui.DialogProgressBG()
        pDialog.create('{} {} '.format(loc(32500), provider), '{} {}'.format('100', loc(32501)))

    for user_item in selected_list['channellist']:
        contentID = user_item['contentId']
        channel_name = user_item['name']
        hzn_data_url = 'https://web-api-pepper.horizon.tv/oesp/v2/{}/web/listings?byStationId={}&byStartTime={}~{}&sort=startTime&range=1-10000'.format(hzndict[grabber][12], contentID, starttime, endtime)
        response = requests.get(hzn_data_url, headers=hzn_header)
        response.raise_for_status()
        hzn_data = response.json()
        broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))
        with open(broadcast_files, 'w') as playbill:
            json.dump(hzn_data, playbill)

        ## Create a List with downloaded channels
        last_channel_name = '{}\n'.format(channel_name)
        with open(list, 'a') as f:
            f.write(last_channel_name)

        if not multi:
            items = sum(1 for f in os.listdir(provider_temppath) if f.endswith('_broadcast.json'))
            percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
            percent_completed = int(100) * int(items) / int(items_to_download)
            pDialog.update(int(percent_completed), '{} {} '.format(loc(32500), channel_name), '{} {} {}'.format(int(percent_remain), loc(32501), provider))
            if int(items) == int(items_to_download):
                log('{} {}'.format(provider, loc(32363)), xbmc.LOGNOTICE)
                break
    if not multi:
        pDialog.close()

def create_xml_channels(grabber):
    provider_temppath, hzn_genres_json, hzn_channels_json, hzn_genres_warnings_tmp, hzn_genres_warnings, hzn_channels_warnings_tmp, hzn_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, hzn_chlist_provider_tmp, hzn_chlist_provider, hzn_chlist_selected, provider, lang = get_settings(grabber)
    log('{} {}'.format(provider, loc(32362)), xbmc.LOGNOTICE)
    if channel_format == 'rytec':
        ## Save hzn_channels.json to Disk
        rytec_file = requests.get(hzn_channels_url).json()
        with open(hzn_channels_json, 'w') as rytec_list:
            json.dump(rytec_file, rytec_list)

    with open(hzn_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('{} {} '.format(loc(32502),provider), '{} {}'.format('100',loc(32501)))

    ## Create XML Channels Provider information
    xml_structure.xml_channels_start(provider)

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        channel_name = user_item['name']
        channel_icon = user_item['pictures'][0]['href']
        channel_id = channel_name
        pDialog.update(int(percent_completed), '{} {} '.format(loc(32502),channel_name),'{} {} {}'.format(int(percent_remain),loc(32501),provider))
        if str(percent_completed) == str(100):
            log('{} {}'.format(provider,loc(32364)), xbmc.LOGNOTICE)

        ## Map Channels
        if not channel_id == '':
            channel_id = mapper.map_channels(channel_id, channel_format, hzn_channels_json, hzn_channels_warnings_tmp, lang)

        ## Create XML Channel Information with provided Variables
        xml_structure.xml_channels(channel_name, channel_id, channel_icon, lang)
    pDialog.close()

def create_xml_broadcast(grabber, enable_rating_mapper, thread_temppath, download_threads):
    provider_temppath, hzn_genres_json, hzn_channels_json, hzn_genres_warnings_tmp, hzn_genres_warnings, hzn_channels_warnings_tmp, hzn_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, hzn_chlist_provider_tmp, hzn_chlist_provider, hzn_chlist_selected, provider, lang = get_settings(grabber)
    hzndict = get_hzndict(grabber)

    download_multithread(thread_temppath, download_threads,grabber, hzn_chlist_selected, provider, provider_temppath, hzndict, days_to_grab)
    log('{} {}'.format(provider,loc(32365)), xbmc.LOGNOTICE)

    if genre_format == 'eit':
        ## Save hzn_genres.json to Disk
        genres_file = requests.get(hzn_genres_url).json()
        with open(hzn_genres_json, 'w') as genres_list:
            json.dump(genres_file, genres_list)

    with open(hzn_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('{} {} '.format(loc(32503),provider), '{} Prozent verbleibend'.format('100'))

    ## Create XML Broadcast Provider information
    xml_structure.xml_broadcast_start(provider)

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        contentID = user_item['contentId']
        channel_name = user_item['name']
        channel_id = channel_name
        pDialog.update(int(percent_completed), '{} {} '.format(loc(32503),channel_name),'{} {} {}'.format(int(percent_remain),loc(32501),provider))
        if str(percent_completed) == str(100):
            log('{} {}'.format(provider,loc(32366)), xbmc.LOGNOTICE)

        broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))
        with open(broadcast_files, 'r') as b:
            broadcastfiles = json.load(b)

        ### Map Channels
        if not channel_id == '':
            channel_id = mapper.map_channels(channel_id, channel_format, hzn_channels_json, hzn_channels_warnings_tmp, lang)

        try:
            for playbilllist in broadcastfiles['listings']:
                try:
                    item_title = playbilllist['program']['title']
                except (KeyError, IndexError):
                    item_title = ''
                try:
                    item_starttime = playbilllist['startTime']
                except (KeyError, IndexError):
                    item_starttime = ''
                try:
                    item_endtime = playbilllist['endTime']
                except (KeyError, IndexError):
                    item_endtime = ''
                try:
                    item_description = playbilllist['program']['longDescription']
                except (KeyError, IndexError):
                    item_description = ''
                try:
                    item_picture = 'https://www.staticwhich.co.uk/static/images/products/no-image/no-image-available.png'
                    found = False
                    asset_types = ['HighResPortrait', 'boxart-xlarge', 'boxart-large', 'boxart-medium', 'tva-poster', 'tva-boxcover']
                    for asset_type in asset_types:
                        for i in range(0, len(playbilllist['program']['images'])):
                            if playbilllist['program']['images'][i]['assetType'] == asset_type:
                                item_picture = playbilllist['program']['images'][i]['url']
                                found = True
                                break
                        if found: break
                    item_picture = item_picture.split('?w')
                    item_picture = item_picture[0]
                except (KeyError, IndexError):
                    item_picture = 'https://www.staticwhich.co.uk/static/images/products/no-image/no-image-available.png'
                try:
                    item_subtitle = playbilllist['program']['secondaryTitle']
                except (KeyError, IndexError):
                    item_subtitle = ''
                genres_list = list()
                try:
                    genre_1 = playbilllist['program']['categories'][0]['title'].replace(',','')
                    genres_list.append(genre_1)
                except (KeyError, IndexError):
                    genre_1 = ''
                try:
                    genre_2 = playbilllist['program']['categories'][1]['title'].replace(',','')
                    genres_list.append(genre_2)
                except (KeyError, IndexError):
                    genre_2 = ''
                try:
                    genre_3 = playbilllist['program']['categories'][2]['title'].replace(',','')
                    genres_list.append(genre_3)
                except (KeyError, IndexError):
                    genre_3 = ''
                try:
                    items_genre = ','.join(genres_list)
                except (KeyError, IndexError):
                    items_genre = ''
                try:
                    item_date = playbilllist['program']['year']
                except (KeyError, IndexError):
                    item_date = ''
                try:
                    item_season = playbilllist['program']['seriesNumber']
                except (KeyError, IndexError):
                    item_season = ''
                try:
                    item_episode = playbilllist['program']['seriesEpisodeNumber']
                except (KeyError, IndexError):
                    item_episode = ''
                try:
                    item_agerating = playbilllist['program']['parentalRating']
                except (KeyError, IndexError):
                    item_agerating = ''
                try:
                    items_director = ','.join(playbilllist['program']['directors'])
                except (KeyError, IndexError):
                    items_director = ''
                try:
                    items_actor = ','.join(playbilllist['program']['cast'])
                except (KeyError, IndexError):
                    items_actor = ''

                # Transform items to Readable XML Format
                item_starrating = ''
                item_country = ''
                items_producer = ''
                if item_agerating == '-1':
                    item_agerating = ''

                if not item_season == '':
                    if int(item_season) >999:
                        item_season = ''
                if not item_episode == '':
                    if int(item_episode) >99999:
                        item_episode = ''

                item_starttime = datetime.utcfromtimestamp(item_starttime / 1000).strftime('%Y%m%d%H%M%S')
                item_endtime = datetime.utcfromtimestamp(item_endtime / 1000).strftime('%Y%m%d%H%M%S')

                # Map Genres
                if not items_genre == '':
                    items_genre = mapper.map_genres(items_genre, genre_format, hzn_genres_json, hzn_genres_warnings_tmp, lang)

                ## Create XML Broadcast Information with provided Variables
                xml_structure.xml_broadcast(episode_format, channel_id, item_title, str(item_starttime), str(item_endtime),
                                            item_description, item_country, item_picture, item_subtitle, items_genre,
                                            item_date, item_season, item_episode, item_agerating, item_starrating, items_director,
                                            items_producer, items_actor, enable_rating_mapper, lang)

        except (KeyError, IndexError):
            log('{} {} {} {} {} {}'.format(provider,loc(32367),channel_name,loc(32368),contentID,loc(32369)))
    pDialog.close()

    ## Create Channel Warnings Textile
    channel_pull = '\nPlease Create an Pull Request for Missing Rytec Id´s to https://github.com/sunsettrack4/config_files/blob/master/hzn_channels.json\n'
    mapper.create_channel_warnings(hzn_channels_warnings_tmp, hzn_channels_warnings, provider, channel_pull)

    ## Create Genre Warnings Textfile
    genre_pull = '\nPlease Create an Pull Request for Missing EIT Genres to https://github.com/sunsettrack4/config_files/blob/master/hzn_genres.json\n'
    mapper.create_genre_warnings(hzn_genres_warnings_tmp, hzn_genres_warnings, provider, genre_pull)

    notify(addon_name, '{} {} {}'.format(loc(32370),provider,loc(32371)), icon=xbmcgui.NOTIFICATION_INFO)
    log('{} {} {}'.format(loc(32370),provider,loc(32371), xbmc.LOGNOTICE))

    if (os.path.isfile(hzn_channels_warnings) or os.path.isfile(hzn_genres_warnings)):
        notify(provider, '{}'.format(loc(32372)), icon=xbmcgui.NOTIFICATION_WARNING)

    ## Delete old Tempfiles, not needed any more
    for file in os.listdir(provider_temppath): xbmcvfs.delete(os.path.join(provider_temppath, file))


def check_provider(grabber,provider_temppath,hzn_chlist_selected,provider):
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(hzn_chlist_selected):
        with open((hzn_chlist_selected), 'w') as selected_list:
            selected_list.write(json.dumps({"channellist": []}))

        ## If no Channellist exist, ask to create one
        yn = OSD.yesno(provider, loc(32405))
        if yn:
            select_channels(grabber)
        else:
            xbmcvfs.delete(hzn_chlist_selected)
            exit()

    ## If a Selected list exist, check valid
    valid = check_selected_list(hzn_chlist_selected)
    if valid is False:
        yn = OSD.yesno(provider, loc(32405))
        if yn:
            select_channels(grabber)
        else:
            xbmcvfs.delete(hzn_chlist_selected)
            exit()

def startup(grabber):
    provider_temppath, hzn_genres_json, hzn_channels_json, hzn_genres_warnings_tmp, hzn_genres_warnings, hzn_channels_warnings_tmp, hzn_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, hzn_chlist_provider_tmp, hzn_chlist_provider, hzn_chlist_selected, provider, lang = get_settings(grabber)
    hzndict = get_hzndict(grabber)
    check_provider(grabber, provider_temppath, hzn_chlist_selected, provider)
    get_channellist(grabber, hzndict, hzn_chlist_provider_tmp, hzn_chlist_provider)

# Channel Selector
try:
    if sys.argv[1] == 'select_channels_hznDE':
        select_channels('de')
    if sys.argv[1] == 'select_channels_hznAT':
        select_channels('at')
    if sys.argv[1] == 'select_channels_hznCH':
        select_channels('ch')
    if sys.argv[1] == 'select_channels_hznNL':
        select_channels('nl')
    if sys.argv[1] == 'select_channels_hznPL':
        select_channels('pl')
    if sys.argv[1] == 'select_channels_hznIE':
        select_channels('ie')
    if sys.argv[1] == 'select_channels_hznGB':
        select_channels('gb')
    if sys.argv[1] == 'select_channels_hznSK':
        select_channels('sk')
    if sys.argv[1] == 'select_channels_hznCZ':
        select_channels('cz')
    if sys.argv[1] == 'select_channels_hznHU':
        select_channels('hu')
    if sys.argv[1] == 'select_channels_hznRO':
        select_channels('ro')

except IndexError:
    pass