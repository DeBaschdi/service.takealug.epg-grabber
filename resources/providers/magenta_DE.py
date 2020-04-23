# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import json
import os
import requests.cookies
import requests
import datetime
from resources.lib import xml_structure

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
tkm_genres_warnings = os.path.join(provider_temppath, 'tkm_genres_warnings.txt')
tkm_channels_warnings = os.path.join(provider_temppath, 'tkm_channels_warnings.txt')

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


magenta_session_cookie = os.path.join(provider_temppath, 'cookies.json')
magenta_chlist_url_disk= os.path.join(provider_temppath, 'chlist_url.json')

magenta_login_url = 'https://web.magentatv.de/EPG/JSON/Login?&T=PC_firefox_75'
magenta_authenticate_url = 'https://web.magentatv.de/EPG/JSON/Authenticate?SID=firstup&T=PC_firefox_75'
magenta_channellist_url = 'https://web.magentatv.de/EPG/JSON/AllChannel?SID=first&T=PC_firefox_75'
magenta_data_url = 'https://web.magentatv.de/EPG/JSON/PlayBillList?userContentFilter=241221015&sessionArea=1&SID=ottall&T=PC_firefox_75'
                    

magenta_login = {'userId':'Guest','mac':'00:00:00:00:00:00'}
magenta_authenticate = {'terminalid':'00:00:00:00:00:00','mac':'00:00:00:00:00:00','terminaltype':'WEBTV','utcEnable':'1','timezone':'UTC','userType':'3','terminalvendor':'Unknown','preSharedKeyID':'PC01P00002','cnonce':'5c6ff0b9e4e5efb1498e7eaa8f54d9fb'}
magenta_get_chlist = {'properties':[{'name':'logicalChannel','include':'/channellist/logicalChannel/contentId,/channellist/logicalChannel/type,/channellist/logicalChannel/name,/channellist/logicalChannel/chanNo,/channellist/logicalChannel/pictures/picture/imageType,/channellist/logicalChannel/pictures/picture/href,/channellist/logicalChannel/foreignsn,/channellist/logicalChannel/externalCode,/channellist/logicalChannel/sysChanNo,/channellist/logicalChannel/physicalChannels/physicalChannel/mediaId,/channellist/logicalChannel/physicalChannels/physicalChannel/fileFormat,/channellist/logicalChannel/physicalChannels/physicalChannel/definition'}],'metaDataVer':'Channel/1.1','channelNamespace':'2','filterlist':[{'key':'IsHide','value':'-1'}],'returnSatChannel':'0'}
magenta_header = {'Host': 'web.magentatv.de',
         'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
         'Accept-Encoding': 'gzip, deflate, br',
         'Connection': 'keep-alive',
         'Upgrade-Insecure-Requests': '1'}

## Login and Authenticate to web.magenta.tv
def magenta_session():
    session = requests.Session()
    session.post(magenta_login_url, data=json.dumps(magenta_login), headers=magenta_header)
    session.post(magenta_authenticate_url, data=json.dumps(magenta_authenticate), headers=magenta_header)
    ## Save Cookies to Disk
    with open(magenta_session_cookie, 'w') as f:
        json.dump(requests.utils.dict_from_cookiejar(session.cookies), f)
    f.close    

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
    with open(magenta_chlist_url_disk, 'w') as channels_url:
        json.dump(response, channels_url)
    channels_url.close
    f.close

def download_broadcastfiles():
    magenta_session()
    session = requests.Session()
    ## Load Cookies from Disk
    with open(magenta_session_cookie, 'r') as f:
        session.cookies = requests.utils.cookiejar_from_dict(json.load(f))
    magenta_CSRFToken = session.cookies["CSRFSESSION"]
    session.headers.update({'X_CSRFToken': magenta_CSRFToken})
    
    with open(magenta_chlist_url_disk, 'r') as s:
        chlist_url = json.load(s)
    
    items_to_download = chlist_url['counttotal']
    items = 0
    print items_to_download +' Broadcastfiles to be downloaded '
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Downloading Broadcast Files for {} {}'.format('', provider),'{} Prozent verbleibend'.format('100'))
    for chlist_url in chlist_url['channellist']:
        items += 1 
        channel = chlist_url['contentId']
        magenta_data = {'channelid': channel ,'type':'2','offset':'0','count':'-1','isFillProgram':'1','properties':'[{"name":"playbill","include":"ratingForeignsn,id,channelid,name,subName,starttime,endtime,cast,casts,country,producedate,ratingid,pictures,type,introduce,foreignsn,seriesID,genres,subNum,seasonNum"}]','endtime': endtime + '235959','begintime': starttime + '000000'}  
        magenta_playbil_url = session.post(magenta_data_url, data=json.dumps(magenta_data), headers=magenta_header)
        magenta_playbil_url.raise_for_status()
        response = magenta_playbil_url.json()
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        broadcast_files = os.path.join(provider_temppath, channel +'_broadcast.json')
        with open(broadcast_files, 'w') as playbill:
            json.dump(response, playbill)
        pDialog.update(percent_completed, 'Downloading Broadcast Files for ' + chlist_url['name'] + ' ' + provider,'{} Prozent verbleibend'.format(percent_remain))
    pDialog.close()
    f.close
    s.close

def create_magenta_xml_channels():
    if channel_format == 'rytec':
        ## Save tkm_channels.json to Disk
        tkm_channels_response = requests.get(tkm_channels_url).json()
        with open(tkm_channels_json, 'w') as tkm_channels:
            json.dump(tkm_channels_response, tkm_channels)
        tkm_channels.close()

    with open(magenta_chlist_url_disk, 'r') as c:
        chlist_url = json.load(c)
    items_to_download = chlist_url['counttotal']
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Create XML Channels for {} {}'.format('', provider),'{} Prozent verbleibend'.format('100'))
    for chlist_url in chlist_url['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download)
        channel_name = chlist_url['name']
        channel_icon = chlist_url['pictures'][0]['href']
        channel_id = channel_name
        pDialog.update(percent_completed, 'Create XML Channels for ' + channel_name + ' ' + provider,'{} Prozent verbleibend'.format(percent_remain))
        print str(percent_completed) + '%' + ' Creating XML EPG Channels for ' + chlist_url['name']

        ## Map Channels
        if not channel_id == '':
            channel_id = map_channels(channel_id)

        ## Create XML Channel Information with provided Variables
        xml_structure.xml_channels(channel_name, channel_id, channel_icon)
    c.close()
    pDialog.close()

def map_genres(items_genre):
    if genre_format == 'eit':
        with open(tkm_genres_json, 'r') as c:
            eit_genre = json.load(c)
        genrelist = items_genre.split(',')
        for genre in genrelist:
            if (genre) not in eit_genre['categories']['DE']:
                log(genre + ' is not in EIT List', xbmc.LOGNOTICE)
                genres_mapped = items_genre
            else:
                genre_mapped = eit_genre['categories']['DE'][genre]
                genres_mapped = items_genre.replace(genre,genre_mapped)

        c.close()
        return str(genres_mapped)

    elif genre_format == 'provider':
        genres_mapped = items_genre
        return str(genres_mapped)

def map_channels(channel_id):
    if channel_format == 'rytec':
        with open(tkm_channels_json, 'r') as c:
            rytec_id = json.load(c)

        if (channel_id) not in rytec_id['channels']['DE']:
            log(channel_id + ' is not in Rytec List', xbmc.LOGNOTICE)
            channels_mapped = channel_id
        else :
            channel_mapped = rytec_id['channels']['DE'][channel_id]
            channels_mapped = channel_id.replace(channel_id, channel_mapped)

        c.close()
        return str(channels_mapped)

    elif channel_format == 'provider':
        channels_mapped = channel_id
        return str(channels_mapped)

def create_magenta_xml_broadcast():
    if genre_format == 'eit':
        ## Save tkm_genres.json to Disk
        tkm_genres_response = requests.get(tkm_genres_url).json()
        with open(tkm_genres_json, 'w') as tkm_genres:
            json.dump(tkm_genres_response, tkm_genres)
        tkm_genres.close()

    with open(magenta_chlist_url_disk, 'r') as c:
        chlist_url = json.load(c)
    items_to_download = chlist_url['counttotal']
    items = 0
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Create XML Broadcast for {} {}'.format('', provider),'{} Prozent verbleibend'.format('100'))
    for chlist_url in chlist_url['channellist']:
        items += 1
        percent_remain = int(100) - int(items) * int(100) / int(items_to_download)
        percent_completed = int(100) * int(items) / int(items_to_download) 
        channel = chlist_url['contentId']
        channel_name = chlist_url['name']
        channel_id = channel_name
        pDialog.update(percent_completed, 'Create XML Broadcast for ' + channel_name + ' ' + provider,'{} Prozent verbleibend'.format(percent_remain))
        print str(percent_completed) + '%' + ' Creating XML EPG Broadcast for ' + chlist_url['name']
        broadcast_files = os.path.join(provider_temppath, channel + '_broadcast.json')
        with open(broadcast_files, 'r') as b:
            broadcastfiles = json.load(b)

        ### Map Channels
        if not channel_id == '':
            channel_id = map_channels(channel_id)

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

                ## Map Genres
                if not items_genre == '':
                    items_genre = map_genres(items_genre)

                ## Create XML Broadcast Information with provided Variables
                xml_structure.xml_broadcast(episode_format, channel_id, item_title, item_starttime, item_endtime, item_description, item_country, item_picture, item_subtitle, items_genre, item_date, item_season, item_episode, item_agerating, items_director, items_producer, items_actor)
        except (KeyError, IndexError):
            print 'no Programminformation for Channel ' + chlist_url['name'] +' with ID '+ chlist_url['contentId'] + ' avaivible'
    pDialog.close()
    c.close
    b.close
    notify(addon_name, 'EPG for Provider ' + provider + ' Grabbed!', icon=xbmcgui.NOTIFICATION_INFO)

def startup():
    ## Create Provider Temppath if not exist
    if not os.path.exists(provider_temppath):
        os.makedirs(provider_temppath)

    magenta_get_channellist()
    download_broadcastfiles()
    xml_structure.xml_channels_start(provider)
    create_magenta_xml_channels()
    xml_structure.xml_broadcast_start(provider)
    create_magenta_xml_broadcast()
