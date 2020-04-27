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
import datetime
from resources.lib import xml_structure
from resources.lib import channel_selector
from resources.lib import mapper

provider = 'MAGENTA TV (DE)'

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")
provider_temppath = os.path.join(temppath, "magenta")

## MAPPING Variables Thx @ sunsettrack4
tkm_genres_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/tkm_genres.json'
tkm_genres_json = os.path.join(provider_temppath, 'tkm_genres.json')
tkm_channels_url = 'https://raw.githubusercontent.com/sunsettrack4/config_files/master/tkm_channels.json'
tkm_channels_json = os.path.join(provider_temppath, 'tkm_channels.json')

## Log Files
tkm_genres_warnings_tmp = os.path.join(provider_temppath, 'tkm_genres_warnings.txt')
tkm_genres_warnings = os.path.join(temppath, 'tkm_genres_warnings.txt')
tkm_channels_warnings_tmp = os.path.join(provider_temppath, 'tkm_channels_warnings.txt')
tkm_channels_warnings = os.path.join(temppath, 'tkm_channels_warnings.txt')

## Read Magenta Settings
days_to_grab = ADDON.getSetting('magenta_days_to_grab')
episode_format = ADDON.getSetting('magenta_episode_format')
channel_format = ADDON.getSetting('magenta_channel_format')
genre_format = ADDON.getSetting('magenta_genre_format')

# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)

# Make OSD Notify Messages
OSD = xbmcgui.Dialog()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

now = datetime.datetime.now()
then = now + datetime.timedelta(days=int(days_to_grab))
starttime = now.strftime("%Y%m%d")
endtime = then.strftime("%Y%m%d")

## Channel Files
magenta_chlist_provider = os.path.join(provider_temppath, 'chlist_magenta_provider.json')
magenta_chlist_selected = os.path.join(datapath, 'chlist_magenta_selected.json')

magenta_login_url = 'https://web.magentatv.de/EPG/JSON/Login?&T=PC_firefox_75'
magenta_authenticate_url = 'https://web.magentatv.de/EPG/JSON/Authenticate?SID=firstup&T=PC_firefox_75'
magenta_channellist_url = 'https://web.magentatv.de/EPG/JSON/AllChannel?SID=first&T=PC_firefox_75'
magenta_data_url = 'https://web.magentatv.de/EPG/JSON/PlayBillList?userContentFilter=241221015&sessionArea=1&SID=ottall&T=PC_firefox_75'
                    

magenta_login = {'userId':'Guest','mac':'00:00:00:00:00:00'}
magenta_authenticate = {'terminalid':'00:00:00:00:00:00','mac':'00:00:00:00:00:00','terminaltype':'WEBTV','utcEnable':'1','timezone':'UTC','userType':'3','terminalvendor':'Unknown','preSharedKeyID':'PC01P00002','cnonce':'5c6ff0b9e4e5efb1498e7eaa8f54d9fb'}
magenta_get_chlist = {'properties':[{'name':'logicalChannel','include':'/channellist/logicalChannel/contentId,/channellist/logicalChannel/name,/channellist/logicalChannel/pictures/picture/imageType,/channellist/logicalChannel/pictures/picture/href'}],'metaDataVer':'Channel/1.1','channelNamespace':'2','filterlist':[{'key':'IsHide','value':'-1'}],'returnSatChannel':'0'}
magenta_header = {'Host': 'web.magentatv.de',
         'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
         'Accept-Encoding': 'gzip, deflate, br',
         'Connection': 'keep-alive',
         'Upgrade-Insecure-Requests': '1'}
magenta_session_cookie = os.path.join(provider_temppath, 'cookies.json')

## Login and Authenticate to web.magenta.tv
def magenta_session():
    session = requests.Session()
    session.post(magenta_login_url, data=json.dumps(magenta_login), headers=magenta_header)
    session.post(magenta_authenticate_url, data=json.dumps(magenta_authenticate), headers=magenta_header)
    ## Save Cookies to Disk
    with open(magenta_session_cookie, 'w') as f:
        json.dump(requests.utils.dict_from_cookiejar(session.cookies), f)

## Get channel list(url) 
def magenta_get_channellist():
    magenta_session()
    session = requests.Session()
    ## Load Cookies from Disk
    with open(magenta_session_cookie, 'r') as f:
        session.cookies = requests.utils.cookiejar_from_dict(json.load(f))

    magenta_CSRFToken = session.cookies["CSRFSESSION"]
    session.headers.update({'X_CSRFToken': magenta_CSRFToken})
    magenta_chlist_url = session.post(magenta_channellist_url, data=json.dumps(magenta_get_chlist), headers=magenta_header)
    magenta_chlist_url.raise_for_status()
    response = magenta_chlist_url.json()

    with open(magenta_chlist_provider, 'w') as provider_list:
        json.dump(response, provider_list)

def magenta_select_channels():
    ## Download chlist_magenta_provider.json
    magenta_get_channellist()
    dialog = xbmcgui.Dialog()

    with open(magenta_chlist_provider, 'r') as o:
        provider_list = json.load(o)

    with open(magenta_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    ## Start Channel Selector
    user_select = channel_selector.select_channels(provider,provider_list,selected_list)

    if user_select is not None:
        with open(magenta_chlist_selected, 'w') as f:
            json.dump(user_select, f, indent=4)
        if os.path.isfile(magenta_chlist_selected):
            ok = dialog.ok(provider, 'New Channellist saved!')
    else:
        log('user list not modified')
        ok = dialog.ok(provider, 'Channellist unchanged!')

def download_broadcastfiles():
    magenta_session()
    session = requests.Session()
    ## Load Cookies from Disk
    with open(magenta_session_cookie, 'r') as f:
        session.cookies = requests.utils.cookiejar_from_dict(json.load(f))
    magenta_CSRFToken = session.cookies["CSRFSESSION"]
    session.headers.update({'X_CSRFToken': magenta_CSRFToken})
    
    with open(magenta_chlist_selected, 'r') as s:
        selected_list = json.load(s)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    log(provider + ' ' + items_to_download +' Broadcastfiles to be downloaded... ', xbmc.LOGNOTICE)
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Downloading Broadcast Files for {} {}'.format('', provider),'{} Prozent verbleibend'.format('100'))
    for user_item in selected_list['channellist']:
        items += 1 
        channel = user_item['contentId']
        magenta_data = {'channelid': channel ,'type':'2','offset':'0','count':'-1','isFillProgram':'1','properties':'[{"name":"playbill","include":"ratingForeignsn,id,channelid,name,subName,starttime,endtime,cast,casts,country,producedate,ratingid,pictures,type,introduce,foreignsn,seriesID,genres,subNum,seasonNum"}]','endtime': endtime + '235959','begintime': starttime + '000000'}  
        magenta_playbil_url = session.post(magenta_data_url, data=json.dumps(magenta_data), headers=magenta_header)
        magenta_playbil_url.raise_for_status()
        response = magenta_playbil_url.json()
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        broadcast_files = os.path.join(provider_temppath, channel +'_broadcast.json')
        with open(broadcast_files, 'w') as playbill:
            json.dump(response, playbill)
        pDialog.update(percent_completed, 'Downloading Broadcast Files for ' + user_item['name'] + ' ' + provider,'{} Prozent verbleibend'.format(percent_remain))
        if str(percent_completed) == str(100):
            log(provider + ' Broadcast Files downloaded', xbmc.LOGNOTICE)
    pDialog.close()

def create_magenta_xml_channels():
    log(provider + ' Create XML Channels...', xbmc.LOGNOTICE)
    if channel_format == 'rytec':
        ## Save tkm_channels.json to Disk
        tkm_channels_response = requests.get(tkm_channels_url).json()
        with open(tkm_channels_json, 'w') as tkm_channels:
            json.dump(tkm_channels_response, tkm_channels)
        tkm_channels.close()

    with open(magenta_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Create XML Channels for {} {}'.format('', provider),'{} Prozent verbleibend'.format('100'))

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
            channel_id = mapper.map_channels(channel_id, channel_format,tkm_channels_json,tkm_channels_warnings_tmp)

        ## Create XML Channel Information with provided Variables
        xml_structure.xml_channels(channel_name, channel_id, channel_icon)
    pDialog.close()

def create_magenta_xml_broadcast(enable_rating_mapper):
    log(provider + ' Create XML EPG Broadcast...', xbmc.LOGNOTICE)
    if genre_format == 'eit':
        ## Save tkm_genres.json to Disk
        tkm_genres_response = requests.get(tkm_genres_url).json()
        with open(tkm_genres_json, 'w') as tkm_genres:
            json.dump(tkm_genres_response, tkm_genres)
        tkm_genres.close()

    with open(magenta_chlist_selected, 'r') as c:
        selected_list = json.load(c)

    #items_to_download = user_item['counttotal']
    items_to_download = str(len(selected_list['channellist']))
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Create XML Broadcast for {} {}'.format('', provider),'{} Prozent verbleibend'.format('100'))
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
            channel_id = mapper.map_channels(channel_id, channel_format,tkm_channels_json,tkm_channels_warnings_tmp)

        try :
            for playbilllist in broadcastfiles['playbilllist']:       
                try:
                    item_title = playbilllist['name']
                except (KeyError, IndexError):
                    item_title = ''
                try:        
                    item_starttime = playbilllist['starttime']
                except (KeyError, IndexError):
                    item_starttime = ''
                try:        
                    item_endtime = playbilllist['endtime']
                except (KeyError, IndexError):
                    item_endtime = ''
                try:        
                    item_description = playbilllist['introduce']
                except (KeyError, IndexError):
                    item_description = ''
                try:        
                    item_country = playbilllist['country']
                except (KeyError, IndexError):
                    item_country = ''
                try:        
                    item_picture = playbilllist['pictures'][1]['href']
                except (KeyError, IndexError):
                    item_picture = ''
                try:        
                    item_subtitle = playbilllist['subName']
                except (KeyError, IndexError):
                    item_subtitle = ''
                try:        
                    items_genre = playbilllist['genres']
                except (KeyError, IndexError):
                    items_genre = ''
                try:        
                    item_date = playbilllist['producedate']
                except (KeyError, IndexError):
                    item_date = ''
                try:        
                    item_season = playbilllist['seasonNum']
                except (KeyError, IndexError):
                    item_season = ''
                try:        
                    item_episode = playbilllist['subNum']
                except (KeyError, IndexError):
                    item_episode = ''
                try:
                    item_agerating = playbilllist['ratingid']
                except (KeyError, IndexError):
                    item_agerating = ''
                try:
                    items_director = playbilllist['cast']['director']
                except (KeyError, IndexError):
                    items_director = ''
                try:
                    items_producer = playbilllist['cast']['producer']
                except (KeyError, IndexError):
                    items_producer = ''
                try:
                    items_actor = playbilllist['cast']['actor']
                except (KeyError, IndexError):
                    items_actor = ''

                # Transform items to Readable XML Format
                if not item_date == '':
                    item_date = item_date.split('-')
                    item_date = item_date[0]
                if (not item_starttime == '' and not item_endtime == ''):
                    start = item_starttime.split(' UTC')
                    item_starttime = start[0].replace(' ', '').replace('-', '').replace(':', '')
                    stop = item_endtime.split(' UTC')
                    item_endtime = stop[0].replace(' ', '').replace('-', '').replace(':', '')
                if not item_country == '':
                    item_country = item_country.upper()
                if item_agerating == '-1':
                    item_agerating = ''

                # Map Genres
                if not items_genre == '':
                    items_genre = mapper.map_genres(items_genre,genre_format,tkm_genres_json,tkm_genres_warnings_tmp)

                ## Create XML Broadcast Information with provided Variables
                xml_structure.xml_broadcast(episode_format, channel_id, item_title, item_starttime, item_endtime, item_description, item_country, item_picture, item_subtitle, items_genre, item_date, item_season, item_episode, item_agerating, items_director, items_producer, items_actor, enable_rating_mapper)

        except (KeyError, IndexError):
            log(provider + ' no Programminformation for Channel ' + user_item['name'] +' with ID '+ user_item['contentId'] + ' avaivible')
    pDialog.close()

    ## Create Channel Warnings Textile
    channel_pull = '\n' + 'Please Create an Pull Request for Missing Rytec Id´s to https://github.com/sunsettrack4/config_files/blob/master/tkm_channels.json' + '\n'
    mapper.create_channel_warnings(tkm_channels_warnings_tmp, tkm_channels_warnings, provider, channel_pull)

    ## Create Genre Warnings Textfile
    genre_pull = '\n' + 'Please Create an Pull Request for Missing EIT Genres to https://github.com/sunsettrack4/config_files/blob/master/tkm_genres.json' + '\n'
    mapper.create_genre_warnings(tkm_genres_warnings_tmp, tkm_genres_warnings, provider, genre_pull)

    notify(addon_name, 'EPG for Provider ' + provider + ' Grabbed!', icon=xbmcgui.NOTIFICATION_INFO)
    log(provider + ' EPG Grabbed!', xbmc.LOGNOTICE)
    xbmc.sleep(4000)

    if (os.path.isfile(tkm_channels_warnings) or os.path.isfile(tkm_genres_warnings)):
        notify(addon_name, 'Warnings Found, please check Logfile', icon=xbmcgui.NOTIFICATION_WARNING)
        xbmc.sleep(3000)

    ## Delete old Tempfiles, not needed any more
    for file in os.listdir(provider_temppath): xbmcvfs.delete(os.path.join(provider_temppath, file))

def check_provider():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    ## Create empty (Selected) Channel List if not exist
    if not os.path.isfile(magenta_chlist_selected):
        with open((magenta_chlist_selected), 'w') as selected_list:
            selected_list.write(json.dumps({}))
            selected_list.close()
        yn = OSD.yesno(provider, "No channel list currently configured, Do you want to create one ?")
        if yn:
            magenta_select_channels()
        else:
            xbmcvfs.delete(magenta_chlist_selected)
            exit()

def startup():
    check_provider()
    magenta_get_channellist()
    download_broadcastfiles()

# Channel Selector
try:
    if sys.argv[1] == 'select_channels':
        magenta_select_channels()
except IndexError:
    pass