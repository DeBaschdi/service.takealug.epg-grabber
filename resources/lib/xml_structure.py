# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

import os
import datetime

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
loc = ADDON.getLocalizedString
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

def xml_channels(channel_name, channel_id, channel_icon, lang):
    channels = []
    channels.append('<channel id="' + channel_id + '">' + '\n')
    channels.append('  <display-name lang="' + lang + '">' + channel_name + '</display-name>' + '\n')
    channels.append('  <icon src="' + channel_icon + '" />' + '\n')
    channels.append('</channel>' + '\n')
    s = ''.join(channels).replace('&','&amp;').decode('utf-8')
    with open(guide_temp,'ab') as f:
        f.write(s)

def xml_broadcast_start(provider):
    start = '\n' + '<!--  ' + provider + ' PROGRAMME LIST -->'
    with open(guide_temp,'ab') as f:
        f.write(start)

def xml_broadcast(episode_format, channel_id, item_title, item_starttime, item_endtime, item_description, item_country, item_picture, item_subtitle, items_genre, item_date, item_season, item_episode, item_agerating, items_director, items_producer, items_actor, enable_rating_mapper, lang):
    guide = []
    guide.append('\n')
    
    ## Programme Condition
    if (not item_starttime == '' and not item_endtime == ''):
        guide.append('<programme start="' + item_starttime + ' +0000" stop="' + item_endtime + ' +0000" channel="' + channel_id + '">' + '\n')
    
    ## IMAGE Condition
    if not item_picture == '':
        guide.append('  <icon src="' + item_picture +'"/>' + '\n')
    
    ## TITLE Condition
    if not item_title == '':
        guide.append('  <title lang="' + lang + '">' + item_title + '</title>' + '\n')
    
    ## SUBTITLE Condition
    if not item_subtitle == '':
        guide.append('  <sub-title lang="' + lang + '">' + item_subtitle +'</sub-title>' + '\n')
    
    ## DESCRIPTION Condition
    if not item_description == '':
        if enable_rating_mapper == False:
            guide.append('  <desc lang="' + lang + '">' + item_description + '</desc>' + '\n')

        ## Rating Mapper
        elif enable_rating_mapper == True:
            if (not item_date == '' and not item_country == '' and not item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + ' • ' + 'S' + item_season + ' E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and not item_country == '' and not item_agerating == ''  and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + ' • ' + 'S' + item_season + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + ' • ' + 'E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + ' • ' + 'S' + item_season + ' E' + item_episode + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + ' • ' + 'S' + item_season + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + ' • ' + 'E' + item_episode +  '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ') ' + item_date + '\n' + item_description + '</desc>' + '\n')

            elif (item_date == '' and not item_country == '' and not item_agerating == '' and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ')' + ' • ' + 'S' + item_season + ' E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ')' + ' • ' + 'E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and not item_country == '' and not item_agerating == '' and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ')' + ' • ' + 'S' + item_season + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ')' + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and not item_country == '' and item_agerating == ''  and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ')' + ' • ' + 'S' + item_season + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and not item_country == '' and not item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ')' + ' • ' + 'FSK' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and not item_country == '' and item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + '(' + item_country + ')' + '\n' + item_description + '</desc>' + '\n')


            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + item_date + ' • ' + 'S' + item_season + ' E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and item_country == '' and item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + item_date + ' • ' + 'S' + item_season + ' E' + item_episode + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + item_date + ' • ' + 'S' + item_season + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + item_date + ' • ' + 'E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + item_date + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (not item_date == '' and item_country == '' and item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + item_date + '\n' + item_description + '</desc>' + '\n')

            elif (item_date == '' and item_country == '' and not item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + 'S' + item_season + ' E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and item_country == '' and item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + 'S' + item_season + ' E' + item_episode + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + 'S' + item_season + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and item_country == '' and item_agerating == '' and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + 'S' + item_season + '\n' + item_description + '</desc>' + '\n')

            elif (item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + 'E' + item_episode + ' • ' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and item_country == '' and item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + 'E' + item_episode + ' • ' + '\n' + item_description + '</desc>' + '\n')
            elif (item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="' + lang + '">' + 'FSK ' + item_agerating + '\n' + item_description + '</desc>' + '\n')

            else:
                guide.append('  <desc lang="' + lang + '">' + item_description + '</desc>' + '\n')

    ## GENRE Condition
    if not items_genre == '':
        genrelist = items_genre.split(',')
        for genre in genrelist:
            guide.append('  <category lang="' + lang + '">{}</category>'.format(genre) + '\n')
    
    ## DATE Condition
    if not item_date == '':
        guide.append('  <date>' + item_date + '</date>' + '\n')
    
    ## COUNTRY Condition
    if not item_country == '':
        guide.append('  <country>' + item_country + '</country>' + '\n')
    
    ## EPISODE Condition
    # XMLTV_NS
    if episode_format == 'xmltv_ns':
        if (not item_season == '' and not item_episode == ''):
            item_season_ns = int(item_season) - int(1)
            item_episode_ns = int(item_episode) - int(1)
            guide.append('  <episode-num system="xmltv_ns">' + str(item_season_ns) + ' . ' + str(item_episode_ns) + ' . ' + '</episode-num>' + '\n')
        elif (not item_season == '' and item_episode == ''):
            item_season_ns = int(item_season) - int(1)
            guide.append('  <episode-num system="xmltv_ns">' + str(item_season_ns) + ' . ' + '0' + ' . ' + '</episode-num>' + '\n')
        elif (item_season == '' and not item_episode == ''):
            item_episode_ns = int(item_episode) - int(1)
            guide.append('  <episode-num system="xmltv_ns">' + '0' + ' . ' + str(item_episode_ns) + ' . ' + '</episode-num>' + '\n')
    # ONSCREEN
    elif episode_format == 'onscreen':
        if (not item_season == '' and not item_episode == ''):
            guide.append('  <episode-num system="onscreen">' + 'S' + item_season + ' E' + item_episode + '</episode-num>' + '\n')
        elif (not item_season == '' and item_episode == ''):    
            guide.append('  <episode-num system="onscreen">' + 'S' + item_season + '</episode-num>' + '\n')
        elif (item_season == '' and not item_episode == ''):
            guide.append('  <episode-num system="onscreen">' + 'E' + item_episode + '</episode-num>' + '\n')
    
    ## AGE-RATING Condition
    if (not item_agerating == ''):
        guide.append('  <rating>' + '\n')
        guide.append('      <value>' + item_agerating + '</value>' + '\n')
        guide.append('  </rating>' + '\n')
    
    ## CAST Condition
    producerlist = items_producer.split(',')
    directorlist = items_director.split(',')
    actorlist = items_actor.split(',')
    # Complete
    if (not items_director == '' and not items_producer == '' and not items_actor == ''):
        guide.append('  <credits>' + '\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>'.format(producer) + '\n')
        for director in directorlist:
            guide.append('      <director>{}</director>'.format(director) + '\n')
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>'.format(actor) + '\n')
        guide.append('  </credits>' + '\n')
    # Producer + Director
    elif (not items_director == '' and not items_producer == '' and items_actor == ''):
        guide.append('  <credits>' + '\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>'.format(producer) + '\n')
        for director in directorlist:
            guide.append('      <director>{}</director>'.format(director) + '\n')
        guide.append('  </credits>' + '\n')
    # Director + Actor
    elif (not items_director == '' and items_producer == '' and not items_actor == ''):
        guide.append('  <credits>' + '\n')
        for director in directorlist:
            guide.append('      <director>{}</director>'.format(director) + '\n')
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>'.format(actor) + '\n')
        guide.append('  </credits>' + '\n')
    # Producer + Actor
    elif (items_director == '' and not items_producer == '' and not items_actor == ''):
        guide.append('  <credits>' + '\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>'.format(producer) + '\n')
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>'.format(actor) + '\n')
        guide.append('  </credits>' + '\n')
    # Only Director
    elif (not items_director == '' and items_producer == '' and items_actor == ''):
        guide.append('  <credits>' + '\n')
        for director in directorlist:
            guide.append('      <director>{}</director>'.format(director) + '\n')
        guide.append('  </credits>' + '\n')
    # Only Producer
    if (items_director == '' and not items_producer == '' and items_actor == ''):
        guide.append('  <credits>' + '\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>'.format(producer) + '\n')
        guide.append('  </credits>' + '\n')
    # Only Actor
    if (items_director == '' and items_producer == '' and not items_actor == ''):
        guide.append('  <credits>' + '\n')
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>'.format(actor) + '\n')
        guide.append('  </credits>' + '\n')
    
    guide.append('</programme>' + '\n')
    s = ''.join(guide).replace('&','&amp;').decode('utf-8')
    with open(guide_temp,'ab') as f:
        f.write(s)

def xml_end():
    end = '\n' + '</tv>' + '\n'
    with open(guide_temp,'ab') as f:
        f.write(end)

