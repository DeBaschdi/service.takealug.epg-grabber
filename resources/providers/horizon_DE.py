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
import time
from datetime import timedelta
from datetime import datetime
from resources.lib import xml_structure
from resources.lib import channel_selector
from resources.lib import mapper

provider = 'HORIZON (DE)'
lang = 'de'

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")
provider_temppath = os.path.join(temppath, "horizonDE")

## MAPPING Variables Thx @ sunsettrack4
hzn_genres_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/hzn_genres.json'
hzn_genres_json = os.path.join(provider_temppath, 'hzn_genres.json')
hzn_channels_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/hzn_channels.json'
hzn_channels_json = os.path.join(provider_temppath, 'hzn_channels.json')

## Log Files
hznDE_genres_warnings_tmp = os.path.join(provider_temppath, 'hznDE_genres_warnings.txt')
hznDE_genres_warnings = os.path.join(temppath, 'hznDE_genres_warnings.txt')
hznDE_channels_warnings_tmp = os.path.join(provider_temppath, 'hznDE_channels_warnings.txt')
hznDE_channels_warnings = os.path.join(temppath, 'hznDE_channels_warnings.txt')

## Read Horizon DE Settings
days_to_grab = int(ADDON.getSetting('hznDE_days_to_grab'))
episode_format = ADDON.getSetting('hznDE_episode_format')
channel_format = ADDON.getSetting('hznDE_channel_format')
genre_format = ADDON.getSetting('hznDE_genre_format')


# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)


# Make OSD Notify Messages
OSD = xbmcgui.Dialog()


def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

# Calculate Date and Time in Microsoft Timestamp
now = datetime.now()
calc_today = datetime.now()
calc_today = calc_today.replace(day=calc_today.day, hour=00, minute=00, second=01, microsecond=0)

calc_then = calc_today.replace(day=calc_today.day , hour=23, minute=59, second=59, microsecond=0)
calc_then += timedelta(days=days_to_grab)

try:
    today = calc_today.strftime("%s")
    starttime = str(today) + '000'
except ValueError:
    today = time.mktime(calc_today.timetuple())
    starttime = str(today).replace('.', '') + '00'

try:
    then = calc_then.strftime("%s")
    endtime = str(then) + '000'
except ValueError:
    then = time.mktime(calc_then.timetuple())
    endtime = str(then).replace('.', '') + '00'

## Channel Files
hznDE_chlist_provider_tmp = os.path.join(provider_temppath, 'chlist_hznDE_provider_tmp.json')
hznDE_chlist_provider = os.path.join(provider_temppath, 'chlist_hznDE_provider.json')
hznDE_chlist_selected = os.path.join(datapath, 'chlist_hznDE_selected.json')

hznDE_login_url = 'https://web-api-pepper.horizon.tv'
hznDE_channellist_url = 'https://web-api-pepper.horizon.tv/oesp/v2/DE/deu/web/channels'

hznDE_header = {'Host': 'web-api-pepper.horizon.tv',
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Connection': 'keep-alive',
                  'Upgrade-Insecure-Requests': '1'}

## Get channel list(url)
def get_channellist():
    hznDE_chlist_url = requests.get(hznDE_channellist_url, headers=hznDE_header)
    hznDE_chlist_url.raise_for_status()
    response = hznDE_chlist_url.json()
    with open(hznDE_chlist_provider_tmp, 'w') as provider_list_tmp:
        json.dump(response, provider_list_tmp)

    #### Transform hznDE_chlist_provider_tmp to Standard chlist Format as hznDE_chlist_provider

    # Load Channellist from Provider
    with open(hznDE_chlist_provider_tmp, 'r') as provider_list_tmp:
        hzn_channels = json.load(provider_list_tmp)

    # Create empty new hznDE_chlist_provider
    with open(hznDE_chlist_provider, 'w') as provider_list:
        provider_list.write(json.dumps({"channellist": []}))
        provider_list.close()

    ch_title = ''

    # Load New Channellist from Provider
    with open(hznDE_chlist_provider) as provider_list:
        data = json.load(provider_list)

        temp = data['channellist']

        for channels in hzn_channels['channels']:
            ch_id = channels['stationSchedules'][0]['station']['id']
            ch_title = channels['stationSchedules'][0]['station']['title']
            for image in channels['stationSchedules'][0]['station']['images']:
                if image['assetType'] == 'station-logo-large':
                    hdimage_url = image['url'].split('?w')
                    hdimage = hdimage_url[0]
            ch_title = ch_title.encode('ascii', 'ignore')
            # channel to be appended
            y = {"contentId": ch_id,
                 "name": ch_title,
                 "pictures": [{"href": hdimage}]}

            # appending channels to data['channellist']
            temp.append(y)

    #Save New Channellist from Provider
    with open(hznDE_chlist_provider, 'w') as provider_list:
        json.dump(data, provider_list, indent=4)

def select_channels():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(hznDE_chlist_selected):
        with open(hznDE_chlist_selected, 'w') as selected_list:
            selected_list.write(json.dumps({}))
            selected_list.close()

    ## Download chlist_hznDE_provider.json
    get_channellist()
    dialog = xbmcgui.Dialog()

    with open(hznDE_chlist_provider, 'r') as o:
        provider_list = json.load(o)

    with open(hznDE_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    ## Start Channel Selector
    user_select = channel_selector.select_channels(provider, provider_list, selected_list)

    if user_select is not None:
        with open(hznDE_chlist_selected, 'w') as f:
            json.dump(user_select, f, indent=4)
        if os.path.isfile(hznDE_chlist_selected):
            valid = check_selected_list()
            if valid is True:
                ok = dialog.ok(provider, 'New Channellist saved!')
                log('New Channellist saved!')
            elif valid is False:
                log('no channels selected')
                yn = OSD.yesno(provider, "You need to Select at least 1 Channel!")
                if yn:
                    select_channels()
                else:
                    xbmcvfs.delete(hznDE_chlist_selected)
                    exit()
    else:
        log('user list not modified')
        check_selected_list()
        ok = dialog.ok(provider, 'Channellist unchanged!')

def check_selected_list():
    check = 'invalid'
    with open(hznDE_chlist_selected, 'r') as c:
        selected_list = json.load(c)
    for user_list in selected_list['channellist']:
        if 'contentId' in user_list:
            check = 'valid'
    if check == 'valid':
        return True
    else:
        return False

def download_broadcastfiles():
    with open(hznDE_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    log(provider + ' ' + items_to_download + ' Broadcastfiles to be downloaded... ', xbmc.LOGNOTICE)
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Downloading Broadcast Files for {} {}'.format('', provider), '{} Prozent verbleibend'.format('100'))

    for user_item in selected_list['channellist']:
        items += 1
        channel = user_item['contentId']
        hznDE_data_url = 'https://web-api-pepper.horizon.tv/oesp/v2/DE/deu/web/listings?byStationId=' + channel +'&byStartTime=' + starttime + '~' + endtime + '&sort=startTime&range=1-10000'
        hznDE_data = requests.get(hznDE_data_url, headers=hznDE_header)
        hznDE_data.raise_for_status()
        response = hznDE_data.json()
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        broadcast_files = os.path.join(provider_temppath, channel + '_broadcast.json')

        with open(broadcast_files, 'w') as playbill:
            json.dump(response, playbill)
        pDialog.update(percent_completed, 'Downloading Broadcast Files for ' + user_item['name'] + ' ' + provider,'{} Prozent verbleibend'.format(percent_remain))
        if str(percent_completed) == str(100):
            log(provider + ' Broadcast Files downloaded', xbmc.LOGNOTICE)
    pDialog.close()


def create_xml_channels():
    log(provider + ' Create XML Channels...', xbmc.LOGNOTICE)
    if channel_format == 'rytec':
        ## Save hzn_channels.json to Disk
        rytec_file = requests.get(hzn_channels_url).json()
        with open(hzn_channels_json, 'w') as rytec_list:
            json.dump(rytec_file, rytec_list)
        rytec_list.close()

    with open(hznDE_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Create XML Channels for {} {}'.format('', provider), '{} Prozent verbleibend'.format('100'))

    ## Create XML Channels Provider information
    xml_structure.xml_channels_start(provider)

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        channel_name = user_item['name']
        channel_icon = user_item['pictures'][0]['href']
        channel_id = channel_name
        pDialog.update(percent_completed, 'Create XML Channels for ' + channel_name + ' ' + provider,'{} Prozent verbleibend'.format(percent_remain))
        if str(percent_completed) == str(100):
            log(provider + ' XML Channels Created', xbmc.LOGNOTICE)

        ## Map Channels
        if not channel_id == '':
            channel_id = mapper.map_channels(channel_id, channel_format, hzn_channels_json, hznDE_channels_warnings_tmp, lang)

        ## Create XML Channel Information with provided Variables
        xml_structure.xml_channels(channel_name, channel_id, channel_icon, lang)
    pDialog.close()


def create_xml_broadcast(enable_rating_mapper):
    log(provider + ' Create XML EPG Broadcast...', xbmc.LOGNOTICE)
    if genre_format == 'eit':
        ## Save hzn_genres.json to Disk
        genres_file = requests.get(hzn_genres_url).json()
        with open(hzn_genres_json, 'w') as genres_list:
            json.dump(genres_file, genres_list)
        genres_list.close()

    with open(hznDE_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Create XML Broadcast for {} {}'.format('', provider), '{} Prozent verbleibend'.format('100'))

    ## Create XML Broadcast Provider information
    xml_structure.xml_broadcast_start(provider)

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        channel = user_item['contentId']
        channel_name = user_item['name']
        channel_id = channel_name
        pDialog.update(percent_completed, 'Create XML Broadcast for ' + channel_name + ' ' + provider,'{} Prozent verbleibend'.format(percent_remain))
        if str(percent_completed) == str(100):
            log(provider + ' XML EPG Broadcast Created', xbmc.LOGNOTICE)

        broadcast_files = os.path.join(provider_temppath, channel + '_broadcast.json')
        with open(broadcast_files, 'r') as b:
            broadcastfiles = json.load(b)

        ### Map Channels
        if not channel_id == '':
            channel_id = mapper.map_channels(channel_id, channel_format, hzn_channels_json, hznDE_channels_warnings_tmp, lang)

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
                    item_country = playbilllist['program']['dummy_country']
                except (KeyError, IndexError):
                    item_country = ''
                try:
                    for image in playbilllist['program']['images']:
                        if image['assetType'] == 'boxart-xlarge':
                            hd_boxart_url = image['url'].split('?w')
                            hd_boxart = hd_boxart_url[0]
                    item_picture = hd_boxart
                except (KeyError, IndexError):
                    item_picture = ''
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
                    items_producer = playbilllist['program']['dummy_producer']
                except (KeyError, IndexError):
                    items_producer = ''
                try:
                    items_actor = ','.join(playbilllist['program']['cast'])
                except (KeyError, IndexError):
                    items_actor = ''

                # Transform items to Readable XML Format
                if not item_country == '':
                    item_country = item_country.upper()
                if item_agerating == '-1':
                    item_agerating = ''

                item_starttime = datetime.utcfromtimestamp(item_starttime / 1000).strftime('%Y%m%d%H%M%S')
                item_endtime = datetime.utcfromtimestamp(item_endtime / 1000).strftime('%Y%m%d%H%M%S')

                # Map Genres
                if not items_genre == '':
                    items_genre = mapper.map_genres(items_genre, genre_format, hzn_genres_json, hznDE_genres_warnings_tmp, lang)

                ## Create XML Broadcast Information with provided Variables
                xml_structure.xml_broadcast(episode_format, channel_id, item_title, str(item_starttime), str(item_endtime),
                                            item_description, item_country, item_picture, item_subtitle, items_genre,
                                            item_date, item_season, item_episode, item_agerating, items_director,
                                            items_producer, items_actor, enable_rating_mapper, lang)

        except (KeyError, IndexError):
            log(provider + ' no Programminformation for Channel ' + user_item['name'] + ' with ID ' + user_item['contentId'] + ' avaivible')
    pDialog.close()

    ## Create Channel Warnings Textile
    channel_pull = '\n' + 'Please Create an Pull Request for Missing Rytec Id´s to https://github.com/sunsettrack4/config_files/blob/master/hzn_channels.json' + '\n'
    mapper.create_channel_warnings(hznDE_channels_warnings_tmp, hznDE_channels_warnings, provider, channel_pull)

    ## Create Genre Warnings Textfile
    genre_pull = '\n' + 'Please Create an Pull Request for Missing EIT Genres to https://github.com/sunsettrack4/config_files/blob/master/hzn_genres.json' + '\n'
    mapper.create_genre_warnings(hznDE_genres_warnings_tmp, hznDE_genres_warnings, provider, genre_pull)

    notify(addon_name, 'EPG for Provider ' + provider + ' Grabbed!', icon=xbmcgui.NOTIFICATION_INFO)
    log(provider + ' EPG Grabbed!', xbmc.LOGNOTICE)
    xbmc.sleep(4000)

    if (os.path.isfile(hznDE_channels_warnings) or os.path.isfile(hznDE_genres_warnings)):
        notify(addon_name, 'Warnings Found, please check Logfile', icon=xbmcgui.NOTIFICATION_WARNING)
        xbmc.sleep(3000)

    ## Delete old Tempfiles, not needed any more
    for file in os.listdir(provider_temppath): xbmcvfs.delete(os.path.join(provider_temppath, file))


def check_provider():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(hznDE_chlist_selected):
        with open((hznDE_chlist_selected), 'w') as selected_list:
            selected_list.write(json.dumps({}))
            selected_list.close()
        yn = OSD.yesno(provider, "No channel list currently configured, Do you want to create one ?")
        if yn:
            select_channels()
        else:
            xbmcvfs.delete(hznDE_chlist_selected)
            exit()


def startup():
    check_provider()
    get_channellist()
    download_broadcastfiles()


# Channel Selector
try:
    if sys.argv[1] == 'select_channels_hznDE':
        select_channels()
except IndexError:
    pass