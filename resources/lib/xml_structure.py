# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

import os
import datetime

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")

now = datetime.datetime.now()
guide_temp = os.path.join(temppath, 'guide.xml')

def xml_start():
    copyright = '<?xml version="1.0" encoding="UTF-8" ?>' + '\n' + '<!-- EPG XMLTV FILE CREATED BY Take-a-LUG TEAM- (c) 2020 Bastian Kleinschmidt -->' + '\n' + '<!-- created on ' + str(now) + ' -->' + '\n' + '<tv>' + '\n'
    with open(guide_temp,'wb') as f:
        f.write(copyright)

def xml_channels_start(provider):
    start = '\n' + '<!--  ' + provider + ' CHANNEL LIST -->' + '\n'
    with open(guide_temp,'ab') as f:
        f.write(start)

def xml_channels(channel_name, channel_id, channel_icon):
    l = []
    l.append('<channel id="' + channel_id + '">' + '\n')
    l.append('  <display-name lang="de">' + channel_name + '</display-name>' + '\n')
    l.append('  <icon src="' + channel_icon + '" />' + '\n')
    l.append('</channel>' + '\n')
    s = ''.join(l).replace('&','&amp;')
    with open(guide_temp,'ab') as f:
        f.write(s)

def xml_broadcast_start(provider):
    start = '\n' + '<!--  ' + provider + ' PROGRAMME LIST -->' + '\n'
    with open(guide_temp,'ab') as f:
        f.write(start)

def xml_broadcast(episode_format, channel_id, item_title, item_starttime, item_endtime, item_description, item_country, item_picture, item_subtitle, items_genre, item_date, item_season, item_episode, item_agerating, items_director, items_producer, items_actor):
    l = []
    l.append('\n')
    
    ## Programme Condition
    if (not item_starttime == '' and not item_endtime == ''):
        start = item_starttime.split(' UTC')
        start = start[0].replace(' ','').replace('-','').replace(':','')
        stop = item_endtime.split(' UTC')
        stop = stop[0].replace(' ','').replace('-','').replace(':','')
        l.append('<programme start="' + start + ' +0000" stop="' + stop + ' +0000" channel="' + channel_id + '">' + '\n')
    
    ## IMAGE Condition
    if not item_picture == '':
        l.append('  <icon src="' + item_picture +'"/>' + '\n')
    
    ## TITLE Condition
    if not item_title == '':
        l.append('  <title lang="de">' + item_title + '</title>' + '\n')
    
    ## SUBTITLE Condition
    if not item_subtitle == '':
        l.append('  <sub-title lang="de">' + item_subtitle +'</sub-title>' + '\n')
    
    ## DESCRIPTION Condition
    if not item_description == '':
        l.append('  <desc lang="de">' + item_description + '</desc>' + '\n')
    
    ## GENRE Condition
    if not items_genre == '':
        genrelist = items_genre.split(',')
        for genre in genrelist:
            l.append('  <category lang="de">{}</category>'.format(genre) + '\n')
    
    ## DATE Condition
    if not item_date == '':
        item_date = item_date.split('-')
        l.append('  <date>' + item_date[0] + '</date>' + '\n')
    
    ## COUNTRY Condition
    if not item_country == '':
        item_country = item_country.upper()
        l.append('  <country>' + item_country + '</country>' + '\n')
    
    ## EPISODE Condition
    # XMLTV_NS
    if episode_format == 'xmltv_ns':
        if (not item_season == '' and not item_episode == ''):
            item_season_ns = int(item_season) - int(1)
            item_episode_ns = int(item_episode) - int(1)
            l.append('  <episode-num system="xmltv_ns">' + str(item_season_ns) + ' . ' + str(item_episode_ns) + ' . ' + '</episode-num>' + '\n')
        elif (not item_season == '' and item_episode == ''):
            item_season_ns = int(item_season) - int(1)
            l.append('  <episode-num system="xmltv_ns">' + str(item_season_ns) + ' . ' + '0' + ' . ' + '</episode-num>' + '\n')
        elif (item_season == '' and not item_episode == ''):
            item_episode_ns = int(item_episode) - int(1)
            l.append('  <episode-num system="xmltv_ns">' + '0' + ' . ' + str(item_episode_ns) + ' . ' + '</episode-num>' + '\n')
    # ONSCREEN
    elif episode_format == 'onscreen':
        if (not item_season == '' and not item_episode == ''):
            l.append('  <epis</tv>ode-num system="onscreen">' + 'S' + item_season + 'E' + ' ' + item_episode + '</episode-num>' + '\n')
        elif (not item_season == '' and item_episode == ''):    
            l.append('  <epis</tv>ode-num system="onscreen">' + 'S' + item_season + '</episode-num>' + '\n')
        elif (item_season == '' and not item_episode == ''):
            l.append('  <episode-num system="onscreen">' + 'E' + item_episode + '</episode-num>' + '\n')
    
    ## AGE-RATING Condition
    if (not item_agerating == '' and not item_agerating == '-1'):
        l.append('  <rating>' + '\n')
        l.append('      <value>' + item_agerating + '</value>' + '\n')
        l.append('  </rating>' + '\n')
    
    ## CAST Condition
    producerlist = items_producer.split(',')
    directorlist = items_director.split(',')
    actorlist = items_actor.split(',')
    # Complete
    if (not items_director == '' and not items_producer == '' and not items_actor == ''):
        l.append('  <credits>' + '\n')
        for producer in producerlist:
            l.append('      <producer>{}</producer>'.format(producer) + '\n')
        for director in directorlist:
            l.append('      <director>{}</director>'.format(director) + '\n')
        for actor in actorlist:    
            l.append('      <actor>{}</actor>'.format(actor) + '\n')
        l.append('  </credits>' + '\n')
    # Producer + Director
    elif (not items_director == '' and not items_producer == '' and items_actor == ''):
        l.append('  <credits>' + '\n')
        for producer in producerlist:
            l.append('      <producer>{}</producer>'.format(producer) + '\n')
        for director in directorlist:
            l.append('      <director>{}</director>'.format(director) + '\n')
        l.append('  </credits>' + '\n')
    # Director + Actor
    elif (not items_director == '' and items_producer == '' and not items_actor == ''):
        l.append('  <credits>' + '\n')
        for director in directorlist:
            l.append('      <director>{}</director>'.format(director) + '\n')
        for actor in actorlist:    
            l.append('      <actor>{}</actor>'.format(actor) + '\n')
        l.append('  </credits>' + '\n')
    # Producer + Actor
    elif (items_director == '' and not items_producer == '' and not items_actor == ''):
        l.append('  <credits>' + '\n')
        for producer in producerlist:
            l.append('      <producer>{}</producer>'.format(producer) + '\n')
        for actor in actorlist:    
            l.append('      <actor>{}</actor>'.format(actor) + '\n')
        l.append('  </credits>' + '\n')
    # Only Director
    elif (not items_director == '' and items_producer == '' and items_actor == ''):
        l.append('  <credits>' + '\n')
        for director in directorlist:
            l.append('      <director>{}</director>'.format(director) + '\n')
        l.append('  </credits>' + '\n')
    # Only Producer
    if (items_director == '' and not items_producer == '' and items_actor == ''):
        l.append('  <credits>' + '\n')
        for producer in producerlist:
            l.append('      <producer>{}</producer>'.format(producer) + '\n')
        l.append('  </credits>' + '\n')
    # Only Actor
    if (items_director == '' and items_producer == '' and not items_actor == ''):
        l.append('  <credits>' + '\n')
        for actor in actorlist:    
            l.append('      <actor>{}</actor>'.format(actor) + '\n')
        l.append('  </credits>' + '\n')
    
    l.append('</programme>' + '\n')
    s = ''.join(l).replace('&','&amp;')
    with open(guide_temp,'ab') as f:
        f.write(s)

def xml_end():
    end = '\n' + '</tv>' + '\n'
    with open(guide_temp,'ab') as f:
        f.write(end)

