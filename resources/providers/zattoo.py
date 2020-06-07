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
import re
from datetime import datetime
from resources.lib import xml_structure
from resources.lib import channel_selector
from resources.lib import mapper
from resources.lib import filesplit

def get_zttdict(grabber):
    ## 0=provider, 1=lang, 2=temppath, 3=genre_warnings, 4=channel_warnings, 5=days_to_grab, 6=episode_format, 7=channel_format, 8=genre_format, 9=chlist_provider_tmp, 10=chlist_provider, 11=chlist_selected, 12=url, 13=Session, 14=Username 15=Password
    zttdict = dict({'ztt_de': ['ZATTOO (DE)', 'de', 'zattooDE', 'zttDE_genres_warnings.txt', 'zttDE_channels_warnings.txt', 'zttDE_days_to_grab', 'zttDE_episode_format', 'zttDE_channel_format', 'zttDE_genre_format', 'chlist_zttDE_provider_tmp.json', 'chlist_zttDE_provider.json', 'chlist_zttDE_selected.json', 'zattoo.com', 'zttDE_session.json', 'zttDE_username', 'zttDE_password'],
                    'ztt_ch': ['ZATTOO (CH)', 'ch', 'zattooCH', 'zttCH_genres_warnings.txt', 'zttCH_channels_warnings.txt', 'zttCH_days_to_grab', 'zttCH_episode_format', 'zttCH_channel_format', 'zttCH_genre_format', 'chlist_zttCH_provider_tmp.json', 'chlist_zttCH_provider.json', 'chlist_zttCH_selected.json', 'zattoo.com', 'zttCH_session.json', 'zttCH_username', 'zttCH_password'],
                    '1und1_de': ['1&1 TV (DE)', 'de', '1und1DE', '1und1DE_genres_warnings.txt', '1und1DE_channels_warnings.txt', '1und1DE_days_to_grab', '1und1DE_episode_format', '1und1DE_channel_format', '1und1DE_genre_format', 'chlist_1und1DE_provider_tmp.json', 'chlist_1und1DE_provider.json', 'chlist_1und1DE_selected.json', 'www.1und1.tv', '1und1DE_session.json', '1und1DE_username', '1und1DE_password'],
                    'ql_ch': ['Quickline Mobil-TV (CH)', 'ch', 'qlCH', 'qlCH_genres_warnings.txt', 'qlCH_channels_warnings.txt', 'qlCH_days_to_grab', 'qlCH_episode_format', 'qlCH_channel_format', 'qlCH_genre_format', 'chlist_qlCH_provider_tmp.json', 'chlist_qlCH_provider.json', 'chlist_qlCH_selected.json', 'mobiltv.quickline.com', 'qlCH_session.json', 'qlCH_username', 'qlCH_password'],
                    'mnet_de': ['M-net TVplus (DE)', 'de', 'mnetDE', 'mnetDE_genres_warnings.txt', 'mnetDE_channels_warnings.txt', 'mnetDE_days_to_grab', 'mnetDE_episode_format', 'mnetDE_channel_format', 'mnetDE_genre_format', 'chlist_mnetDE_provider_tmp.json', 'chlist_mnetDE_provider.json', 'chlist_mnetDE_selected.json', 'tvplus.m-net.de', 'mnetDE_session.json', 'mnetDE_username', 'mnetDE_password'],
                    'walytv_ch': ['WALY.TV (CH)', 'ch', 'walyCH', 'walyCH_genres_warnings.txt', 'walyCH_channels_warnings.txt', 'walyCH_days_to_grab', 'walyCH_episode_format', 'walyCH_channel_format', 'walyCH_genre_format', 'chlist_walyCH_provider_tmp.json', 'chlist_walyCH_provider.json', 'chlist_walyCH_selected.json', 'player.waly.tv', 'walyCH_session.json', 'walyCH_username', 'walyCH_DE_password'],
                    'meinewelt_at': ['Meine Welt unterwegs (AT)', 'at', 'mweltAT', 'mweltAT_genres_warnings.txt', 'mweltAT_channels_warnings.txt', 'mweltAT_days_to_grab', 'mweltAT_episode_format', 'mweltAT_channel_format', 'mweltAT_genre_format', 'chlist_mweltAT_provider_tmp.json', 'chlist_mweltAT_provider.json', 'chlist_mweltAT_selected.json', 'www.meinewelt.cc', 'mweltAT_session.json', 'mweltAT_username', 'mweltAT_password'],
                    'bbtv_de': ['BBV TV (DE)', 'de', 'bbvDE', 'bbvDE_genres_warnings.txt', 'bbvDE_channels_warnings.txt', 'bbvDE_days_to_grab', 'bbvDE_episode_format', 'bbvDE_channel_format', 'bbvDE_genre_format', 'chlist_bbvDE_provider_tmp.json', 'chlist_bbvDE_provider.json', 'chlist_bbvDE_selected.json', 'www.bbv-tv.net', 'bbvDE_session.json', 'bbvDE_username', 'bbvDE_password'],
                    'vtxtv_ch': ['VTX TV (CH)', 'ch', 'vtxCH', 'vtxCH_genres_warnings.txt', 'vtxCH_channels_warnings.txt', 'vtxCH_days_to_grab', 'vtxCH_episode_format', 'vtxCH_channel_format', 'vtxCH_genre_format', 'chlist_vtxCH_provider_tmp.json', 'chlist_vtxCH_provider.json', 'chlist_vtxCH_selected.json', 'www.vtxtv.ch', 'vtxCH_session.json', 'vtxCH_username', 'vtxCH_password'],
                    'myvision_ch': ['myVision mobile TV (CH)', 'ch', 'myvisCH', 'myvisCH_genres_warnings.txt', 'myvisCH_channels_warnings.txt', 'myvisCH_days_to_grab', 'myvisCH_episode_format', 'myvisCH_channel_format', 'myvisCH_genre_format', 'chlist_myvisCH_provider_tmp.json', 'chlist_myvisCH_provider.json', 'chlist_myvisCH_selected.json', 'www.myvisiontv.ch', 'myvisCH_session.json', 'myvisCH_username', 'myvisCH_password'],
                    'glattvision_ch': ['Glattvision+ (CH)', 'ch', 'gvisCH', 'gvisCH_genres_warnings.txt', 'gvisCH_channels_warnings.txt', 'gvisCH_days_to_grab', 'gvisCH_episode_format', 'gvisCH_channel_format', 'gvisCH_genre_format', 'chlist_gvisCH_provider_tmp.json', 'chlist_gvisCH_provider.json', 'chlist_gvisCH_selected.json', 'wiptv.glattvision.ch', 'gvisCH_session.json', 'gvisCH_username', 'gvisCH_password'],
                    'sak_ch': ['SAK TV (CH)', 'ch', 'sakCH', 'sakCH_genres_warnings.txt', 'sakCH_channels_warnings.txt', 'sakCH_days_to_grab', 'sakCH_episode_format', 'sakCH_channel_format', 'sakCH_genre_format', 'chlist_sakCH_provider_tmp.json', 'chlist_sakCH_provider.json', 'chlist_sakCH_selected.json', 'www.saktv.ch', 'sakCH_session.json', 'sakCH_username', 'sakCH_password'],
                    'nettv_de': ['Net TV (DE)', 'de', 'nettvDE', 'nettvDE_genres_warnings.txt', 'nettvDE_channels_warnings.txt', 'nettvDE_days_to_grab', 'nettvDE_episode_format', 'nettvDE_channel_format', 'nettvDE_genre_format', 'chlist_nettvDE_provider_tmp.json', 'chlist_nettvDE_provider.json', 'chlist_nettvDE_selected.json', 'nettv.netcologne.de', 'nettvDE_session.json', 'nettvDE_username', 'nettvDE_password'],
                    'tvoewe_de': ['EWE TV App (DE)', 'de', 'eweDE', 'eweDE_genres_warnings.txt', 'eweDE_channels_warnings.txt', 'eweDE_days_to_grab', 'eweDE_episode_format', 'eweDE_channel_format', 'eweDE_genre_format', 'chlist_eweDE_provider_tmp.json', 'chlist_eweDE_provider.json', 'chlist_eweDE_selected.json', 'tvonline.ewe.de', 'eweDE_session.json', 'eweDE_username', 'eweDE_password'],
                    'quantum_ch': ['Quantum TV (CH)', 'ch', 'qttvCH', 'qttvCH_genres_warnings.txt', 'qttvCH_channels_warnings.txt', 'qttvCH_days_to_grab', 'qttvCH_episode_format', 'qttvCH_channel_format', 'qttvCH_genre_format', 'chlist_qttvCH_provider_tmp.json', 'chlist_qttvCH_provider.json', 'chlist_qttvCH_selected.json', 'www.quantum-tv.com', 'qttvCH_session.json', 'qttvCH_username', 'qttvCH_password'],
                    'salt_ch': ['Salt TV (CH)', 'ch', 'saltCH', 'saltCH_genres_warnings.txt', 'saltCH_channels_warnings.txt', 'saltCH_days_to_grab', 'saltCH_episode_format', 'saltCH_channel_format', 'saltCH_genre_format', 'chlist_saltCH_provider_tmp.json', 'chlist_saltCH_provider.json', 'chlist_saltCH_selected.json', 'tv.salt.ch', 'saltCH_session.json', 'saltCH_username', 'saltCH_password'],
                    'tvoswe_de': ['SWB TV App (DE)', 'de', 'swbDE', 'swbDE_genres_warnings.txt', 'swbDE_channels_warnings.txt', 'swbDE_days_to_grab', 'swbDE_episode_format', 'swbDE_channel_format', 'swbDE_genre_format', 'chlist_swbDE_provider_tmp.json', 'chlist_swbDE_provider.json', 'chlist_swbDE_selected.json', 'tvonline.swb-gruppe.de', 'swbDE_session.json', 'swbDE_username', 'swbDE_password'],
                    'eir_ie': ['eir TV (IE)', 'ie', 'eirIE', 'eirIE_genres_warnings.txt', 'eirIE_channels_warnings.txt', 'eirIE_days_to_grab', 'eirIE_episode_format', 'eirIE_channel_format', 'eirIE_genre_format', 'chlist_eirIE_provider_tmp.json', 'chlist_eirIE_provider.json', 'chlist_eirIE_selected.json', 'tv.eir.ie', 'eirIE_session.json', 'eirIE_username', 'eirIE_password'],
                  })
    return zttdict

def get_settings(grabber):
    zttdict = get_zttdict(grabber)
    provider_temppath = os.path.join(temppath, zttdict[grabber][2])

    # EIT Genre + Rytec Format Mapping Files
    ztt_genres_json = os.path.join(provider_temppath, 'ztt_genres.json')
    ztt_channels_json = os.path.join(provider_temppath, 'ztt_channels.json')

    ## Log Files
    ztt_genres_warnings_tmp = os.path.join(provider_temppath, zttdict[grabber][3])
    ztt_genres_warnings = os.path.join(temppath, zttdict[grabber][3])
    ztt_channels_warnings_tmp = os.path.join(provider_temppath, zttdict[grabber][4])
    ztt_channels_warnings = os.path.join(temppath, zttdict[grabber][4])

    ## Read Zattoo Settings
    days_to_grab = int(ADDON.getSetting(zttdict[grabber][5]))
    episode_format = ADDON.getSetting(zttdict[grabber][6])
    channel_format = ADDON.getSetting(zttdict[grabber][7])
    genre_format = ADDON.getSetting(zttdict[grabber][8])
    username = ADDON.getSetting(zttdict[grabber][14])
    password = ADDON.getSetting(zttdict[grabber][15])

    ## Session Files
    ztt_session = os.path.join(provider_temppath, zttdict[grabber][13])

    ## Channel Files
    ztt_chlist_provider_tmp = os.path.join(provider_temppath, zttdict[grabber][9])
    ztt_chlist_provider = os.path.join(provider_temppath, zttdict[grabber][10])
    ztt_chlist_selected = os.path.join(datapath, zttdict[grabber][11])

    provider = zttdict[grabber][0]
    lang = zttdict[grabber][1]
    ztt_header = {'Host': '{}'.format(zttdict[grabber][12]),
                  'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Connection': 'keep-alive',
                  'Upgrade-Insecure-Requests': '1'}

    return provider_temppath, ztt_genres_json, ztt_channels_json, ztt_genres_warnings_tmp, ztt_genres_warnings, ztt_channels_warnings_tmp, ztt_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, ztt_chlist_provider_tmp, ztt_chlist_provider, ztt_chlist_selected, provider, lang, ztt_header, ztt_session, username, password

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
ztt_genres_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/ztt_genres.json'
ztt_channels_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/ztt_channels.json'

# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)


# Make OSD Notify Messages
OSD = xbmcgui.Dialog()

# Zapi Settings
ZAPI_UUID = 'd7512e98-38a0-4f01-b820-5a5cf98141fe'
ZAPI_APP_VERSION = '3.2004.2'

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

def get_epgLength(days_to_grab):
    # Calculate Date and Time in Microsoft Timestamp
    today = datetime.today()
    calc_today = datetime(today.year, today.month, today.day, hour=00, minute=00, second=0)

    calc_then = datetime(today.year, today.month, today.day, hour=23, minute=59, second=59)

    try:
        today = calc_today.strftime("%s")
        daystart = '{}'.format(int(today))
    except ValueError:
        today = time.mktime(calc_today.timetuple())
        daystart = '{}'.format(int(today))

    try:
        then = calc_then.strftime("%s")
        dayend = '{}'.format(int(then))
    except ValueError:
        then = time.mktime(calc_then.timetuple())
        dayend = '{}'.format(int(then))

    return daystart, dayend


## Login and Authenticate to Zattoo IPTV Service
def zattoo_session(grabber):
    provider_temppath, ztt_genres_json, ztt_channels_json, ztt_genres_warnings_tmp, ztt_genres_warnings, ztt_channels_warnings_tmp, ztt_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, ztt_chlist_provider_tmp, ztt_chlist_provider, ztt_chlist_selected, provider, lang, header, ztt_session, username, password = get_settings(grabber)
    zttdict = get_zttdict(grabber)
    # Fetch Token
    session = requests.Session()
    session.headers.update(header)
    token_url = 'https://{}/int/'.format(zttdict[grabber][12])
    response = session.get(token_url, headers=header)
    dialog = xbmcgui.Dialog()

    if (username == '' or password == ''):
        ok = dialog.ok(provider, loc(32410))
        if ok:
            log('{} {}'.format(provider, loc(32410)), xbmc.LOGERROR)
        return False
    try:
        token = re.search("window\.appToken\s*=\s*'(.*)'", response.text).group(1)
        found_token = True
    except:
        token_url = 'https://{}/'.format(zttdict[grabber][12])
        response = session.post(token_url, headers=header)
        try:
            token = re.search("window\.appToken\s*=\s*'(.*)'", response.text).group(1)
            found_token = True
        except:
            # Can find Token
            ok = dialog.ok(provider, loc(32411))
            if ok:
                log('{} {}'.format(provider, loc(32411)), xbmc.LOGERROR)
            found_token = False

    if found_token:
        # Announce
        announce_url = 'https://{}/zapi/v2/session/hello'.format(zttdict[grabber][12])
        params = {"client_app_token": token,
                  "uuid": ZAPI_UUID,
                  "lang": "en",
                  "app_version": ZAPI_APP_VERSION,
                  "format": "json"}
        session.post(announce_url, data=params, headers=header)

        # Login
        login_url = 'https://{}/zapi/v2/account/login'.format(zttdict[grabber][12])
        params = {"login": username, "password": password}
        response = session.post(login_url, headers=header, data=params)

        # Wrong Username or Password
        if response.status_code == 400:
            ok = dialog.ok(provider, loc(32410))
            if ok:
                log('{} {}'.format(provider, loc(32410)), xbmc.LOGERROR)
            login = False

        # Invalid Token
        elif response.status_code == 403:
            ok = dialog.ok(provider, loc(32412))
            if ok:
                log('{} {}'.format(provider, loc(32412)), xbmc.LOGERROR)
            login = False

        # Login OK
        elif response.status_code == 200:
            notify(addon_name, '{} {}'.format(loc(32384), provider), icon=xbmcgui.NOTIFICATION_INFO)
            log('{} {}'.format(provider, loc(32384)), xbmc.LOGNOTICE)
            login = True

        # Error while Login (unkown)
        else:
            ok = dialog.ok(provider, '{} Status is = {}'.format(loc(32387), response.status_code))
            if ok:
                log('{} {} Status is = {}'.format(provider, loc(32387), response.status_code), xbmc.LOGERROR)
            login = False

        if login:
            # Save Session to Disk
            beaker_session_id = requests.utils.dict_from_cookiejar(session.cookies)['beaker.session.id']
            power_guide_hash = response.json()['session']['power_guide_hash']

            with open(ztt_session, 'w') as s:
                s.write(json.dumps({"beaker.session.id": beaker_session_id, "power_guide_hash": power_guide_hash}))
            return True
        if not login:
            return False
    if not found_token:
        return False

## Get channel list(url)
def get_channellist(grabber, zttdict, ztt_chlist_provider_tmp, ztt_chlist_provider, header, ztt_session):
    # Load session File
    with open(ztt_session, 'r') as s:
        session_data = json.load(s)

    # get chlist
    ztt_channellist_url = 'https://{}/zapi/v3/cached/{}/channels?'.format(zttdict[grabber][12], session_data['power_guide_hash'])
    response = requests.get(ztt_channellist_url, headers=header, cookies={'beaker.session.id': session_data['beaker.session.id']})
    response.raise_for_status()
    ztt_chlist_url = response.json()

    with open(ztt_chlist_provider_tmp, 'w') as provider_list_tmp:
        json.dump(ztt_chlist_url, provider_list_tmp)

    #### Transform ztt_chlist_provider_tmp to Standard chlist Format as ztt_chlist_provider

    # Load Channellist from Provider
    with open(ztt_chlist_provider_tmp, 'r') as provider_list_tmp:
        ztt_channels = json.load(provider_list_tmp)

    # Create empty new ztt_chlist_provider
    with open(ztt_chlist_provider, 'w') as provider_list:
        provider_list.write(json.dumps({"channellist": []}))

    ch_title = ''

    # Load New Channellist from Provider
    with open(ztt_chlist_provider) as provider_list:
        data = json.load(provider_list)

        temp = data['channellist']

        for channels in ztt_channels['channels']:
            ch_id = channels['cid']
            try:
                found = False
                levels = ['hd', 'sd']
                for level in levels:
                    for i in range(0, len(channels['qualities'])):
                        if channels['qualities'][i]['level'] == level:
                            ch_title = channels['qualities'][i]['title']
                            found = True
                            break
                    if found:
                        break
            except:
                ch_title = channels['title']
            try:
                found = False
                levels = ['hd', 'sd']
                for level in levels:
                    for i in range(0, len(channels['qualities'])):
                        if channels['qualities'][i]['level'] == level:
                            logo_token = channels['qualities'][i]['logo_token']
                            found = True
                            break
                    if found:
                        break
                hdimage = 'https://images.zattic.com/logos/{}/black/210x120.png'.format(logo_token)
            except:
                hdimage = ''

            # channel to be appended
            y = {"contentId": ch_id,
                 "name": ch_title,
                 "pictures": [{"href": hdimage}]}

            # appending channels to data['channellist']
            temp.append(y)

    #Save New Channellist from Provider
    with open(ztt_chlist_provider, 'w') as provider_list:
        json.dump(data, provider_list, indent=4)

def select_channels(grabber):
    provider_temppath, ztt_genres_json, ztt_channels_json, ztt_genres_warnings_tmp, ztt_genres_warnings, ztt_channels_warnings_tmp, ztt_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, ztt_chlist_provider_tmp, ztt_chlist_provider, ztt_chlist_selected, provider, lang, header, ztt_session, username, password = get_settings(grabber)
    zttdict = get_zttdict(grabber)

    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    if zattoo_session(grabber):
        ## Create empty (Selected) Channel List if not exist
        if not os.path.isfile(ztt_chlist_selected):
            with open(ztt_chlist_selected, 'w') as selected_list:
                selected_list.write(json.dumps({"channellist": []}))

        ## Download chlist_provider.json
        get_channellist(grabber, zttdict, ztt_chlist_provider_tmp, ztt_chlist_provider, header, ztt_session)
        dialog = xbmcgui.Dialog()

        with open(ztt_chlist_provider, 'r') as o:
            provider_list = json.load(o)

        with open(ztt_chlist_selected, 'r') as s:
            selected_list = json.load(s)

        ## Start Channel Selector
        user_select = channel_selector.select_channels(provider, provider_list, selected_list)

        if user_select is not None:
            with open(ztt_chlist_selected, 'w') as f:
                json.dump(user_select, f, indent=4)
            if os.path.isfile(ztt_chlist_selected):
                valid = check_selected_list(ztt_chlist_selected)
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
                        xbmcvfs.delete(ztt_chlist_selected)
                        exit()
        else:
            valid = check_selected_list(ztt_chlist_selected)
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
                    xbmcvfs.delete(ztt_chlist_selected)
                    exit()

def check_selected_list(ztt_chlist_selected):
    check = 'invalid'
    with open(ztt_chlist_selected, 'r') as c:
        selected_list = json.load(c)
    for user_list in selected_list['channellist']:
        if 'contentId' in user_list:
            check = 'valid'
    if check == 'valid':
        return True
    else:
        return False

def download_multithread(thread_temppath, download_threads, grabber, ztt_chlist_selected, provider, provider_temppath, zttdict, days_to_grab, header, ztt_session):
    # delete old broadcast files if exist
    for f in os.listdir(provider_temppath):
        if f.endswith('_broadcast.json'):
            xbmcvfs.delete(os.path.join(provider_temppath, f))

    list_done = os.path.join(provider_temppath, 'list.txt')
    splitname = os.path.join(thread_temppath, 'chlist_zttXX_selected')

    with open(ztt_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    if filesplit.split_chlist_selected(thread_temppath, ztt_chlist_selected, splitname, download_threads, enable_multithread):
        multi = True
        needed_threads = sum([len(files) for r, d, files in os.walk(thread_temppath)])
        items_to_download = str(len(selected_list['channellist']))
        log('{} {} {} '.format(provider, items_to_download, loc(32361)), xbmc.LOGNOTICE)
        pDialog = xbmcgui.DialogProgressBG()
        log('{} Multithread({}) Mode'.format(provider, needed_threads), xbmc.LOGNOTICE)
        pDialog.create('{} {} '.format(loc(32500), provider), '{} {}'.format('100', loc(32501)))

        jobs = []
        for thread in range(0, int(needed_threads)):
            p = Process(target=download_thread, args=(grabber, '{}_{}.json'.format(splitname, int(thread)), multi, list_done, provider, provider_temppath, zttdict, days_to_grab, header, ztt_session, ))
            jobs.append(p)
            p.start()
        for j in jobs:
            while j.is_alive():
                xbmc.sleep(100)
                try:
                    last_line = ''
                    with open(list_done, 'r') as f:
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
        download_thread(grabber, ztt_chlist_selected, multi, list_done, provider, provider_temppath, zttdict, days_to_grab, header, ztt_session)

def download_manifest(grabber, days_to_grab, provider_temppath, zttdict, ztt_session, header, provider):
    # Delete old Manifest Files
    for f in os.listdir(provider_temppath):
        if f.startswith('day_'):
            xbmcvfs.delete(os.path.join(provider_temppath, f))

    ## Download Manifest Files
    daystart, dayend = get_epgLength(days_to_grab)
    day_to_start = int(daystart)
    day_to_end = int(dayend)

    # Load session File
    with open(ztt_session, 'r') as s:
        session_data = json.load(s)

    items_to_download = int(days_to_grab)
    items = 1
    log('{} {} {} '.format(provider, items_to_download, loc(32382)), xbmc.LOGNOTICE)
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('{} {} '.format(loc(32504), provider), '{} {}'.format('100', loc(32501)))

    for i in range(0, int(days_to_grab)):
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        mani_files = os.path.join(provider_temppath, 'day_{}.json'.format(i))
        ztt_mani_url = 'https://{}/zapi/v3/cached/{}/guide?start={}&end={}'.format(zttdict[grabber][12], session_data['power_guide_hash'], day_to_start, day_to_end)
        response = requests.get(ztt_mani_url, headers=header, cookies={'beaker.session.id': session_data['beaker.session.id']})
        response.raise_for_status()
        ztt_mani = response.json()

        ## Save Manifest Files To Disk
        with open(mani_files, 'w') as mani:
            json.dump(ztt_mani, mani, indent=4)

        pDialog.update(int(percent_completed), '{} {} '.format(loc(32504), items), '{} {} {}'.format(int(percent_remain), loc(32501), provider))

        day_to_start += int(86400)
        day_to_end += int(86400)

        if i == int(days_to_grab) - 1:
            log('{} {}'.format(provider, loc(32383)), xbmc.LOGNOTICE)
            break
    pDialog.close()

def download_thread(grabber, ztt_chlist_selected, multi, list_done, provider, provider_temppath, zttdict, days_to_grab, header, ztt_session):
    requests.adapters.DEFAULT_RETRIES = 5

    with open(ztt_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    # Load session File
    with open(ztt_session, 'r') as s:
        session_data = json.load(s)

    if not multi:
        items_to_download = str(len(selected_list['channellist']))
        log('{} {} {} '.format(provider, items_to_download, loc(32361)), xbmc.LOGNOTICE)
        pDialog = xbmcgui.DialogProgressBG()
        pDialog.create('{} {} '.format(loc(32500), provider), '{} {}'.format('100', loc(32501)))

    # Download Broadcast Files
    for user_item in selected_list['channellist']:
        contentID = user_item['contentId']
        channel_name = user_item['name']
        broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))


        broadcast_dirtylist = list()
        for i in range(0, int(days_to_grab)):
            with open(os.path.join(provider_temppath, 'day_{}.json'.format(i)), 'r') as s:
                ztt_mani = json.load(s)
            for broadcast in ztt_mani['channels'][contentID]:
                broadcast_id = str(broadcast['id'])
                broadcast_dirtylist.append(broadcast_id)
            broadcast_list = list(set(broadcast_dirtylist))
            broadcast_ids = ','.join(broadcast_list)

            if i == int(days_to_grab) -1:
                break

        if (not len(broadcast_list) == 0 and len(broadcast_list) <= 619):
            try:
                ztt_broadcast_url = 'https://{}/zapi/v2/cached/program/power_details/{}?program_ids={}'.format(zttdict[grabber][12], session_data['power_guide_hash'], broadcast_ids)
                response = requests.get(ztt_broadcast_url, headers=header, cookies={'beaker.session.id': session_data['beaker.session.id']})
                response.raise_for_status()
                ztt_data = response.json()

                ## Save Broadcast Files To Disk
                with open(broadcast_files, 'w') as playbill:
                    json.dump(ztt_data, playbill, indent=4)

            except:
                retries = 5
                attempt = 0
                while retries > 0:
                    attempt += 1
                    log('{} {} ERROR TRY REDOWNLOAD {}'.format(provider, response.status_code, contentID), xbmc.LOGNOTICE)
                    broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))
                    xbmc.sleep(5000)
                    ztt_broadcast_url = 'https://{}/zapi/v2/cached/program/power_details/{}?program_ids={}'.format(zttdict[grabber][12], session_data['power_guide_hash'], broadcast_ids)
                    response = requests.get(ztt_broadcast_url, headers=header, cookies={'beaker.session.id': session_data['beaker.session.id']})
                    response.raise_for_status()

                    ## Save Broadcast Files To Disk
                    with open(broadcast_files, 'w') as f:
                        f.write(response.text)

                    retries -= 1
                    if (os.path.isfile(broadcast_files) and os.stat(broadcast_files).st_size >= 1):
                        log('{} {} REDOWNLOAD success at attemp {}'.format(provider, contentID, attempt), xbmc.LOGNOTICE)
                        break

        elif len(broadcast_list) == 0:
            with open((broadcast_files), 'w') as dummy:
                dummy.write(json.dumps({"no_data": []}))

        elif len(broadcast_list) >= 620:
            log('{} WARNING ZATTOO LIST IS TO LONG {}, splitting in 4 Parts'.format(contentID, len(broadcast_list)), xbmc.LOGDEBUG)
            broadcast_ids_0 = ','.join(broadcast_list[:len(broadcast_list) // 4])
            broadcast_ids_1 = ','.join(broadcast_list[len(broadcast_list) // 4:2 * len(broadcast_list) // 4])
            broadcast_ids_2 = ','.join(broadcast_list[len(broadcast_list) // 2:3 * len(broadcast_list) // 4])
            broadcast_ids_3 = ','.join(broadcast_list[3 * len(broadcast_list) // 4:])

            with open(broadcast_files, 'w') as empty_list:
                empty_list.write(json.dumps({"programs": []}))

            with open(broadcast_files) as playbill:
                data = json.load(playbill)
                temp = data['programs']

            for i in range(0, 4):
                if i == 0:
                    broadcast_ids = broadcast_ids_0
                elif i == 1:
                    broadcast_ids = broadcast_ids_1
                elif i == 2:
                    broadcast_ids = broadcast_ids_2
                elif i == 3:
                    broadcast_ids = broadcast_ids_3
                broadcast_files = os.path.join(provider_temppath, '{}_broadcast.json'.format(contentID))
                ztt_broadcast_url = 'https://{}/zapi/v2/cached/program/power_details/{}?program_ids={}'.format(zttdict[grabber][12], session_data['power_guide_hash'], broadcast_ids)
                response = requests.get(ztt_broadcast_url, headers=header, cookies={'beaker.session.id': session_data['beaker.session.id']})
                response.raise_for_status()
                ztt_data = response.json()

                for broadcast in ztt_data['programs']:
                    # broadcasts to be appended
                    y = broadcast

                    # appending Broadcasts to data['programs']
                    temp.append(y)

            ## Save Broadcast Files To Disk
            with open(broadcast_files, 'w') as playbill:
                json.dump(data, playbill, indent=4)

        ## Create a List with downloaded channels
        last_channel_name = '{}\n'.format(channel_name)
        with open(list_done, 'a') as f:
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
    provider_temppath, ztt_genres_json, ztt_channels_json, ztt_genres_warnings_tmp, ztt_genres_warnings, ztt_channels_warnings_tmp, ztt_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, ztt_chlist_provider_tmp, ztt_chlist_provider, ztt_chlist_selected, provider, lang, header, ztt_session, username, password = get_settings(grabber)
    log('{} {}'.format(provider, loc(32362)), xbmc.LOGNOTICE)
    if channel_format == 'rytec':
        ## Save ztt_channels.json to Disk
        rytec_file = requests.get(ztt_channels_url).json()
        with open(ztt_channels_json, 'w') as rytec_list:
            json.dump(rytec_file, rytec_list)

    with open(ztt_chlist_selected, 'r') as c:
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
            channel_id = mapper.map_channels(channel_id, channel_format, ztt_channels_json, ztt_channels_warnings_tmp, lang)

        ## Create XML Channel Information with provided Variables
        xml_structure.xml_channels(channel_name, channel_id, channel_icon, lang)
    pDialog.close()

def create_xml_broadcast(grabber, enable_rating_mapper, thread_temppath, download_threads):
    provider_temppath, ztt_genres_json, ztt_channels_json, ztt_genres_warnings_tmp, ztt_genres_warnings, ztt_channels_warnings_tmp, ztt_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, ztt_chlist_provider_tmp, ztt_chlist_provider, ztt_chlist_selected, provider, lang, header, ztt_session, username, password = get_settings(grabber)
    zttdict = get_zttdict(grabber)

    download_manifest(grabber, days_to_grab, provider_temppath, zttdict, ztt_session, header, provider)
    download_multithread(thread_temppath, download_threads, grabber, ztt_chlist_selected, provider, provider_temppath, zttdict, days_to_grab, header, ztt_session)

    log('{} {}'.format(provider, loc(32365)), xbmc.LOGNOTICE)

    if genre_format == 'eit':
        ## Save ztt_genres.json to Disk
        genres_file = requests.get(ztt_genres_url).json()
        with open(ztt_genres_json, 'w') as genres_list:
            json.dump(genres_file, genres_list)

    with open(ztt_chlist_selected, 'r') as c:
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
            channel_id = mapper.map_channels(channel_id, channel_format, ztt_channels_json, ztt_channels_warnings_tmp, lang)

        try:
            for playbilllist in sorted(broadcastfiles['programs'], key=lambda k: k['s'], reverse=False):
                try:
                    item_title = playbilllist['t']
                except (KeyError, IndexError):
                    item_title = ''
                try:
                    item_starttime = playbilllist['s']
                except (KeyError, IndexError):
                    item_starttime = ''
                try:
                    item_endtime = playbilllist['e']
                except (KeyError, IndexError):
                    item_endtime = ''
                try:
                    item_description = playbilllist['d']
                except (KeyError, IndexError):
                    item_description = ''
                try:
                    item_picture_id = playbilllist['i_t']
                    item_picture = 'http://images.zattic.com/cms/{}/format_1920x1080.jpg'.format(item_picture_id)
                except (KeyError, IndexError):
                    item_picture = 'https://www.staticwhich.co.uk/static/images/products/no-image/no-image-available.png'
                try:
                    item_subtitle = playbilllist['et']
                except (KeyError, IndexError):
                    item_subtitle = ''
                try:
                    genres_list = list()
                    for genre in playbilllist['g']:
                        genres_list.append(genre)
                    items_genre = ','.join(genres_list)
                except (KeyError, IndexError):
                    items_genre = ''
                try:
                    item_date = playbilllist['year']
                except (KeyError, IndexError):
                    item_date = ''
                try:
                    item_country = playbilllist['country']
                except (KeyError, IndexError):
                    item_country = ''
                try:
                    item_season = playbilllist['s_no']
                except (KeyError, IndexError):
                    item_season = ''
                try:
                    item_episode = playbilllist['e_no']
                except (KeyError, IndexError):
                    item_episode = ''
                try:
                    item_agerating = playbilllist['yp_r']
                except (KeyError, IndexError):
                    item_agerating = ''
                try:
                    director_list = list()
                    for director in playbilllist['cr']['director']:
                        director_list.append(director)
                    items_director = ','.join(director_list)
                except (KeyError, IndexError):
                    items_director = ''
                try:
                    actor_list = list()
                    for actor in playbilllist['cr']['actor']:
                        actor_list.append(actor)
                    items_actor = ','.join(actor_list)
                except (KeyError, IndexError):
                    items_actor = ''

                # Transform items to Readable XML Format
                item_starrating = ''
                items_producer = ''
                if item_subtitle == None:
                    item_subtitle = ''
                if item_episode == None:
                    item_episode = ''
                if item_season == None:
                    item_season = ''
                if item_agerating == None:
                    item_agerating = ''

                if not item_season == '':
                    if int(item_season) >999:
                        item_season = ''
                if not item_episode == '':
                    if int(item_episode) >99999:
                        item_episode = ''

                item_starttime = datetime.utcfromtimestamp(item_starttime).strftime('%Y%m%d%H%M%S')
                item_endtime = datetime.utcfromtimestamp(item_endtime).strftime('%Y%m%d%H%M%S')

                # Map Genres
                if not items_genre == '':
                    items_genre = mapper.map_genres(items_genre, genre_format, ztt_genres_json, ztt_genres_warnings_tmp, lang)

                ## Create XML Broadcast Information with provided Variables
                xml_structure.xml_broadcast(episode_format, channel_id, item_title, str(item_starttime), str(item_endtime),
                                            item_description, item_country, item_picture, item_subtitle, items_genre,
                                            item_date, item_season, item_episode, item_agerating, item_starrating, items_director,
                                            items_producer, items_actor, enable_rating_mapper, lang)

        except (KeyError, IndexError):
            log('{} {} {} {} {} {}'.format(provider, loc(32367), channel_name, loc(32368), contentID, loc(32369)))
    pDialog.close()

    ## Create Channel Warnings Textile
    channel_pull = '\nPlease Create an Pull Request for Missing Rytec Id´s to https://github.com/sunsettrack4/config_files/blob/master/ztt_channels.json\n'
    mapper.create_channel_warnings(ztt_channels_warnings_tmp, ztt_channels_warnings, provider, channel_pull)

    ## Create Genre Warnings Textfile
    genre_pull = '\nPlease Create an Pull Request for Missing EIT Genres to https://github.com/sunsettrack4/config_files/blob/master/ztt_genres.json\n'
    mapper.create_genre_warnings(ztt_genres_warnings_tmp, ztt_genres_warnings, provider, genre_pull)

    notify(addon_name, '{} {} {}'.format(loc(32370), provider, loc(32371)), icon=xbmcgui.NOTIFICATION_INFO)
    log('{} {} {}'.format(loc(32370), provider, loc(32371), xbmc.LOGNOTICE))

    if (os.path.isfile(ztt_channels_warnings) or os.path.isfile(ztt_genres_warnings)):
        notify(provider, '{}'.format(loc(32372)), icon=xbmcgui.NOTIFICATION_WARNING)

    ## Delete old Tempfiles, not needed any more
    for file in os.listdir(provider_temppath): xbmcvfs.delete(os.path.join(provider_temppath, file))


def check_provider(grabber, provider_temppath, ztt_chlist_selected, provider):
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(ztt_chlist_selected):
        with open((ztt_chlist_selected), 'w') as selected_list:
            selected_list.write(json.dumps({"channellist": []}))

        ## If no Channellist exist, ask to create one
        yn = OSD.yesno(provider, loc(32405))
        if yn:
            select_channels(grabber)
        else:
            xbmcvfs.delete(ztt_chlist_selected)
            return False

    ## If a Selected list exist, check valid
    valid = check_selected_list(ztt_chlist_selected)
    if valid is False:
        yn = OSD.yesno(provider, loc(32405))
        if yn:
            select_channels(grabber)
        else:
            xbmcvfs.delete(ztt_chlist_selected)
            return False

    if not zattoo_session(grabber):
        return False
    return True

def startup(grabber):
    provider_temppath, ztt_genres_json, ztt_channels_json, ztt_genres_warnings_tmp, ztt_genres_warnings, ztt_channels_warnings_tmp, ztt_channels_warnings, days_to_grab, episode_format, channel_format, genre_format, ztt_chlist_provider_tmp, ztt_chlist_provider, ztt_chlist_selected, provider, lang, header, ztt_session, username, password = get_settings(grabber)
    zttdict = get_zttdict(grabber)

    if check_provider(grabber, provider_temppath, ztt_chlist_selected, provider):
        get_channellist(grabber, zttdict, ztt_chlist_provider_tmp, ztt_chlist_provider, header, ztt_session)
        return True
    else:
        return False

# Channel Selector
try:
    if sys.argv[1] == 'select_channels_zttDE':
        select_channels('ztt_de')
    if sys.argv[1] == 'select_channels_zttCH':
        select_channels('ztt_ch')
    if sys.argv[1] == 'select_channels_1und1DE':
        select_channels('1und1_de')
    if sys.argv[1] == 'select_channels_qlCH':
        select_channels('ql_ch')
    if sys.argv[1] == 'select_channels_mnetDE':
        select_channels('mnet_de')
    if sys.argv[1] == 'select_channels_walyCH':
        select_channels('walytv_ch')
    if sys.argv[1] == 'select_channels_mweltAT':
        select_channels('meinewelt_at')
    if sys.argv[1] == 'select_channels_bbvDE':
        select_channels('bbtv_de')
    if sys.argv[1] == 'select_channels_vtxCH':
        select_channels('vtxtv_ch')
    if sys.argv[1] == 'select_channels_myvisCH':
        select_channels('myvision_ch')
    if sys.argv[1] == 'select_channels_gvisCH':
        select_channels('glattvision_ch')
    if sys.argv[1] == 'select_channels_sakCH':
        select_channels('sak_ch')
    if sys.argv[1] == 'select_channels_nettvDE':
        select_channels('nettv_de')
    if sys.argv[1] == 'select_channels_eweDE':
        select_channels('tvoewe_de')
    if sys.argv[1] == 'select_channels_qttvCH':
        select_channels('quantum_ch')
    if sys.argv[1] == 'select_channels_saltCH':
        select_channels('salt_ch')
    if sys.argv[1] == 'select_channels_swbDE':
        select_channels('tvoswe_de')
    if sys.argv[1] == 'select_channels_eirIE':
        select_channels('eir_ie')
except IndexError:
    pass