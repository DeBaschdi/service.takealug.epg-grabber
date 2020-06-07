# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import json
import os
import sys
import requests.adapters
import requests.cookies
import requests
import re
from datetime import datetime
from datetime import timedelta
from resources.lib import xml_structure
from resources.lib import channel_selector
from resources.lib import mapper
from resources.lib import filesplit

provider = 'SWISSCOM (CH)'
lang = 'ch'


ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
loc = ADDON.getLocalizedString
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")
provider_temppath = os.path.join(temppath, "swcCH")

## Enable Multithread
enable_multithread = True if ADDON.getSetting('enable_multithread').upper() == 'TRUE' else False
if enable_multithread:
    try:
        from multiprocessing import Process
    except:
        pass

## MAPPING Variables Thx @ sunsettrack4
swcCH_genres_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/swc_genres.json'
swcCH_genres_json = os.path.join(provider_temppath, 'swc_genres.json')
swcCH_channels_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/swc_channels.json'
swcCH_channels_json = os.path.join(provider_temppath, 'swc_channels.json')

## Log Files
swcCH_genres_warnings_tmp = os.path.join(provider_temppath, 'swcCH_genres_warnings.txt')
swcCH_genres_warnings = os.path.join(temppath, 'swcCH_genres_warnings.txt')
swcCH_channels_warnings_tmp = os.path.join(provider_temppath, 'swcCH_channels_warnings.txt')
swcCH_channels_warnings = os.path.join(temppath, 'swcCH_channels_warnings.txt')

## Read Swisscom (CH) Settings
days_to_grab = int(ADDON.getSetting('swcCH_days_to_grab'))
episode_format = ADDON.getSetting('swcCH_episode_format')
channel_format = ADDON.getSetting('swcCH_channel_format')
genre_format = ADDON.getSetting('swcCH_genre_format')


# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)


# Make OSD Notify Messages
OSD = xbmcgui.Dialog()


def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)


def get_epgLength():
    # Calculate Date and Time
    today = datetime.today()
    calc_today = datetime(today.year, today.month, today.day, hour=00, minute=00, second=1)

    calc_then = datetime(today.year, today.month, today.day, hour=23, minute=59, second=59)
    calc_then += timedelta(days=days_to_grab)

    starttime = calc_today.strftime("%Y%m%d%H%M")
    endtime = calc_then.strftime("%Y%m%d%H%M")

    return starttime, endtime

#starttime = starttime_day.strftime("%Y-%m-%d")

## Channel Files
swcCH_chlist_provider_tmp = os.path.join(provider_temppath, 'chlist_swcCH_provider_tmp.json')
swcCH_chlist_provider = os.path.join(provider_temppath, 'chlist_swcCH_provider.json')
swcCH_chlist_selected = os.path.join(datapath, 'chlist_swcCH_selected.json')

swcCH_header = {'Host': 'services.sg1.etvp01.sctv.ch',
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
                  'Accept-Encoding': 'gzip',
                  'Connection': 'keep-alive',
                  'Upgrade-Insecure-Requests': '1'}

def get_channellist():
    swcCH_channellist_url = 'https://services.sg2.etvp01.sctv.ch/portfolio/tv/channels'
    swcCH_chlist_url = requests.get(swcCH_channellist_url, headers=swcCH_header)
    swcCH_chlist_url.raise_for_status()
    response = swcCH_chlist_url.json()
    with open(swcCH_chlist_provider_tmp, 'w') as provider_list_tmp:
        json.dump(response, provider_list_tmp)

    #### Transform swcCH_chlist_provider_tmp to Standard chlist Format as swcCH_chlist_provider

    # Load Channellist from Provider
    with open(swcCH_chlist_provider_tmp, 'r') as provider_list_tmp:
        swcCH_channels = json.load(provider_list_tmp)

    # Create empty new swcCH_chlist_provider
    with open(swcCH_chlist_provider, 'w') as provider_list:
        provider_list.write(json.dumps({"channellist": []}))

    ch_title = ''

    # Load New Channellist from Provider
    with open(swcCH_chlist_provider) as provider_list:
        data = json.load(provider_list)

        temp = data['channellist']

        for channels in swcCH_channels:
            ch_id = channels['Identifier']
            ch_title = channels['Title']
            hdimage = 'https://services.sg1.etvp01.sctv.ch/content/images/tv/channel/{}_image_7_w90.png'.format(ch_id)
            # channel to be appended
            y = {"contentId": ch_id,
                 "name": ch_title,
                 "pictures": [{"href": hdimage}]}

            # appending channels to data['channellist']
            temp.append(y)

    #Save New Channellist from Provider
    with open(swcCH_chlist_provider, 'w') as provider_list:
        json.dump(data, provider_list, indent=4)

def select_channels():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(swcCH_chlist_selected):
        with open((swcCH_chlist_selected), 'w') as selected_list:
            selected_list.write(json.dumps({"channellist": []}))

    ## Download chlist_magenta_provider.json
    get_channellist()
    dialog = xbmcgui.Dialog()

    with open(swcCH_chlist_provider, 'r') as o:
        provider_list = json.load(o)

    with open(swcCH_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    ## Start Channel Selector
    user_select = channel_selector.select_channels(provider, provider_list, selected_list)

    if user_select is not None:
        with open(swcCH_chlist_selected, 'w') as f:
            json.dump(user_select, f, indent=4)
        if os.path.isfile(swcCH_chlist_selected):
            valid = check_selected_list()
            if valid is True:
                ok = dialog.ok(provider, loc(32402))
                if ok:
                    log(loc(32402), xbmc.LOGNOTICE)
            elif valid is False:
                log(loc(32403), xbmc.LOGNOTICE)
                yn = OSD.yesno(provider, loc(32403))
                if yn:
                    select_channels()
                else:
                    xbmcvfs.delete(swcCH_chlist_selected)
                    exit()
    else:
        valid = check_selected_list()
        if valid is True:
            ok = dialog.ok(provider, loc(32404))
            if ok:
                log(loc(32404), xbmc.LOGNOTICE)
        elif valid is False:
            log(loc(32403), xbmc.LOGNOTICE)
            yn = OSD.yesno(provider, loc(32403))
            if yn:
                select_channels()
            else:
                xbmcvfs.delete(swcCH_chlist_selected)
                exit()

def check_selected_list():
    check = 'invalid'
    with open(swcCH_chlist_selected, 'r') as c:
        selected_list = json.load(c)
    for user_list in selected_list['channellist']:
        if 'contentId' in user_list:
            check = 'valid'
    if check == 'valid':
        return True
    else:
        return False

def download_multithread(thread_temppath, download_threads):
    # delete old broadcast files if exist
    for f in os.listdir(provider_temppath):
        if f.endswith('_broadcast.json'):
            xbmcvfs.delete(os.path.join(provider_temppath, f))

    list = os.path.join(provider_temppath, 'list.txt')
    splitname = os.path.join(thread_temppath, 'chlist_swcCH_selected')
    starttime, endtime = get_epgLength()

    with open(swcCH_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    if filesplit.split_chlist_selected(thread_temppath, swcCH_chlist_selected, splitname, download_threads, enable_multithread):
        multi = True
        needed_threads = sum([len(files) for r, d, files in os.walk(thread_temppath)])
        items_to_download = str(len(selected_list['channellist']))
        log('{} {} {} '.format(provider, items_to_download, loc(32361)), xbmc.LOGNOTICE)
        pDialog = xbmcgui.DialogProgressBG()
        log('{} Multithread({}) Mode'.format(provider, needed_threads), xbmc.LOGNOTICE)
        pDialog.create('{} {} '.format(loc(32500), provider), '{} {}'.format('100', loc(32501)))

        jobs = []
        for thread in range(0, int(needed_threads)):
            p = Process(target=download_thread, args=('{}_{}.json'.format(splitname, int(thread)), multi, list, starttime, endtime, ))
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
        log('{} {} '.format(provider, 'Can`t download in Multithreading mode, loading single...'), xbmc.LOGNOTICE)
        download_thread(swcCH_chlist_selected, multi, list, starttime, endtime)

def download_thread(chlist_selected, multi, list, starttime, endtime):
    requests.adapters.DEFAULT_RETRIES = 5

    with open(chlist_selected, 'r') as s:
        selected_list = json.load(s)

    if not multi:
        items_to_download = str(len(selected_list['channellist']))
        log('{} {} {} '.format(provider, items_to_download, loc(32361)), xbmc.LOGNOTICE)
        pDialog = xbmcgui.DialogProgressBG()
        pDialog.create('{} {} '.format(loc(32500), provider), '{} {}'.format('100', loc(32501)))

    for user_item in selected_list['channellist']:
        channel_name = user_item['name']
        contentID = user_item['contentId']
        swc_data_url = 'https://services.sg1.etvp01.sctv.ch/catalog/tv/channels/list/end={};ids={};level=normal;start={}'.format(endtime, contentID, starttime)
        response = requests.get(swc_data_url, headers=swcCH_header)
        response.raise_for_status()
        swc_data = response.json()
        broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))
        with open(broadcast_files, 'w') as playbill:
            json.dump(swc_data, playbill)

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

def create_xml_channels():
    log('{} {}'.format(provider,loc(32362)), xbmc.LOGNOTICE)
    if channel_format == 'rytec':
        ## Save swcCH_channels.json to Disk
        swcCH_channels_response = requests.get(swcCH_channels_url).json()
        with open(swcCH_channels_json, 'w') as swcCH_channels:
            json.dump(swcCH_channels_response, swcCH_channels)

    with open(swcCH_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('{} {} '.format(loc(32502), provider), '{} {}'.format('100', loc(32501)))

    ## Create XML Channels Provider information
    xml_structure.xml_channels_start(provider)

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        channel_name = user_item['name']
        channel_icon = user_item['pictures'][0]['href']
        channel_id = channel_name
        pDialog.update(int(percent_completed), '{} {} '.format(loc(32502), channel_name), '{} {} {}'.format(int(percent_remain), loc(32501), provider))
        if str(percent_completed) == str(100):
            log('{} {}'.format(provider,loc(32364)), xbmc.LOGNOTICE)

        ## Map Channels
        if not channel_id == '':
            channel_id = mapper.map_channels(channel_id, channel_format, swcCH_channels_json, swcCH_channels_warnings_tmp, lang)

        ## Create XML Channel Information with provided Variables
        xml_structure.xml_channels(channel_name, channel_id, channel_icon, lang)
    pDialog.close()

def create_xml_broadcast(enable_rating_mapper, thread_temppath, download_threads):

    download_multithread(thread_temppath, download_threads)
    log('{} {}'.format(provider, loc(32365)), xbmc.LOGNOTICE)

    if genre_format == 'eit':
        ## Save hzn_genres.json to Disk
        genres_file = requests.get(swcCH_genres_url).json()
        with open(swcCH_genres_json, 'w') as genres_list:
            json.dump(genres_file, genres_list)

    with open(swcCH_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('{} {} '.format(loc(32503), provider), '{} Prozent verbleibend'.format('100'))

    ## Create XML Broadcast Provider information
    xml_structure.xml_broadcast_start(provider)

    for user_item in selected_list['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        contentID = user_item['contentId']
        channel_name = user_item['name']
        channel_id = channel_name
        pDialog.update(int(percent_completed), '{} {} '.format(loc(32503), channel_name),
                       '{} {} {}'.format(int(percent_remain), loc(32501), provider))
        if str(percent_completed) == str(100):
            log('{} {}'.format(provider, loc(32366)), xbmc.LOGNOTICE)

        broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))
        with open(broadcast_files, 'r') as b:
            broadcastfiles = json.load(b)

        ### Map Channels
        if not channel_id == '':
            channel_id = mapper.map_channels(channel_id, channel_format, swcCH_channels_json, swcCH_channels_warnings_tmp, lang)

        try:
            for playbilllist in broadcastfiles['Nodes']['Items'][0]['Content']['Nodes']['Items']:
                try:
                    item_title = playbilllist['Content']['Description']['Title']
                except (KeyError, IndexError):
                    item_title = ''
                try:
                    item_starttime = playbilllist['Availabilities'][0]['AvailabilityStart']
                except (KeyError, IndexError):
                    item_starttime = ''
                try:
                    item_endtime = playbilllist['Availabilities'][0]['AvailabilityEnd']
                except (KeyError, IndexError):
                    item_endtime = ''
                try:
                    item_description = playbilllist['Content']['Description']['Summary']
                except (KeyError, IndexError):
                    item_description = ''
                try:
                    url = playbilllist['Content']['Nodes']['Items'][0]['ContentPath']
                    item_picture = 'https://services.sg1.etvp01.sctv.ch/content/images{}_w1920.png'.format(url)
                except (KeyError, IndexError):
                    item_picture = ''
                try:
                    item_subtitle = playbilllist['Content']['Description']['Subtitle']
                except (KeyError, IndexError):
                    item_subtitle = ''
                try:
                    items_genre = ''
                    found = False
                    role = ['Genre']
                    for genre in role:
                        for i in range(0, len(playbilllist['Relations'])):
                            if playbilllist['Relations'][i]['Role'] == genre:
                                items_genre = playbilllist['Relations'][i]['TargetIdentifier']
                                found = True
                                break
                        if found: break
                except (KeyError, IndexError):
                    items_genre = ''
                try:
                    item_date = playbilllist['Content']['Description']['ReleaseDate']
                except (KeyError, IndexError):
                    item_date = ''
                try:
                    item_country = playbilllist['Content']['Description']['Country']
                except (KeyError, IndexError):
                    item_country = ''
                try:
                    item_season = playbilllist['Content']['Series']['Season']
                except (KeyError, IndexError):
                    item_season = ''
                try:
                    item_episode = playbilllist['Content']['Series']['Episode']
                except (KeyError, IndexError):
                    item_episode = ''
                try:
                    item_agerating = playbilllist['Content']['Description']['AgeRestrictionRating']
                except (KeyError, IndexError):
                    item_agerating = ''
                try:
                    item_starrating = playbilllist['Content']['Description']['Rating']
                except (KeyError, IndexError):
                    item_starrating = ''
                try:
                    items_director = ''
                    found = False
                    role = ['Director']
                    for director in role:
                        for i in range(0, len(playbilllist['Relations'])):
                            if playbilllist['Relations'][i]['Role'] == director:
                                items_director_fn = playbilllist['Relations'][i]['TargetNode']['Content']['Description']['FirstName']
                                items_director_ln = playbilllist['Relations'][i]['TargetNode']['Content']['Description']['LastName']
                                items_director = '{} {}'.format(items_director_fn, items_director_ln)
                                found = True
                                break
                        if found: break
                except (KeyError, IndexError):
                    items_director = ''
                try:
                    actor_list = list()
                    items_actor = ''
                    found = False
                    role = ['Actor']
                    for actor in role:
                        for i in range(0, len(playbilllist['Relations'])):
                            if playbilllist['Relations'][i]['Role'] == actor:
                                items_actor_fn = playbilllist['Relations'][i]['TargetNode']['Content']['Description']['FirstName']
                                items_actor_ln = playbilllist['Relations'][i]['TargetNode']['Content']['Description']['LastName']
                                item_actor = '{} {}'.format(items_actor_fn, items_actor_ln)
                                actor_list.append(item_actor)
                                found = True
                        if found: break
                    items_actor = ','.join(actor_list)
                except (KeyError, IndexError):
                    items_actor = ''

                # Transform items to Readable XML Format
                if not item_agerating == '':
                    item_agerating = re.sub(r"\D+", '#', item_agerating).split('#')[0]
                if not item_date == '':
                    item_date = item_date.split('-')[0]
                items_producer = ''

                if (not item_starttime == '' and not item_endtime == ''):
                    item_starttime = re.sub(r"\D+", '', item_starttime)
                    item_endtime = re.sub(r"\D+", '', item_endtime)

                # Map Genres
                if not items_genre == '':
                    items_genre = mapper.map_genres(items_genre, genre_format, swcCH_genres_json, swcCH_genres_warnings_tmp, lang)

                ## Create XML Broadcast Information with provided Variables
                xml_structure.xml_broadcast(episode_format, channel_id, item_title, str(item_starttime),
                                            str(item_endtime),
                                            item_description, item_country, item_picture, item_subtitle,
                                            items_genre,
                                            item_date, item_season, item_episode, item_agerating, item_starrating, items_director,
                                            items_producer, items_actor, enable_rating_mapper, lang)

        except (KeyError, IndexError):
            log('{} {} {} {} {} {}'.format(provider, loc(32367), channel_name, loc(32368), contentID, loc(32369)))
    pDialog.close()

    ## Create Channel Warnings Textile
    channel_pull = '\nPlease Create an Pull Request for Missing Rytec Id´s to https://github.com/sunsettrack4/config_files/blob/master/tvs_channels.json\n'
    mapper.create_channel_warnings(swcCH_channels_warnings_tmp, swcCH_channels_warnings, provider, channel_pull)

    ## Create Genre Warnings Textfile
    genre_pull = '\nPlease Create an Pull Request for Missing EIT Genres to https://github.com/sunsettrack4/config_files/blob/master/tvs_genres.json\n'
    mapper.create_genre_warnings(swcCH_genres_warnings_tmp, swcCH_genres_warnings, provider, genre_pull)

    notify(addon_name, '{} {} {}'.format(loc(32370),provider,loc(32371)), icon=xbmcgui.NOTIFICATION_INFO)
    log('{} {} {}'.format(loc(32370),provider,loc(32371), xbmc.LOGNOTICE))

    if (os.path.isfile(swcCH_channels_warnings) or os.path.isfile(swcCH_genres_warnings)):
        notify(provider, '{}'.format(loc(32372)), icon=xbmcgui.NOTIFICATION_WARNING)

    ## Delete old Tempfiles, not needed any more
    for file in os.listdir(provider_temppath): xbmcvfs.delete(os.path.join(provider_temppath, file))


def check_provider():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(swcCH_chlist_selected):
        with open((swcCH_chlist_selected), 'w') as selected_list:
            selected_list.write(json.dumps({"channellist": []}))

        ## If no Channellist exist, ask to create one
        yn = OSD.yesno(provider, loc(32405))
        if yn:
            select_channels()
        else:
            xbmcvfs.delete(swcCH_chlist_selected)
            exit()

    ## If a Selected list exist, check valid
    valid = check_selected_list()
    if valid is False:
        yn = OSD.yesno(provider, loc(32405))
        if yn:
            select_channels()
        else:
            xbmcvfs.delete(swcCH_chlist_selected)
            exit()

def startup():
    check_provider()
    get_channellist()

# Channel Selector
try:
    if sys.argv[1] == 'select_channels_swcCH':
        select_channels()
except IndexError:
    pass