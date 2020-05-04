# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import os
import datetime
import sys

## Python 3 Compatibility
if sys.version_info[0] > 2:
    # python 3
    pass
else:
    # python 2
    import codecs
    def open(file, mode='r', buffering=-1, encoding=None,errors=None, newline=None, closefd=True, opener=None):
        return codecs.open(filename=file, mode=mode, encoding=encoding,errors=errors, buffering=buffering)

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
loc = ADDON.getLocalizedString
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")

now = datetime.datetime.now()
guide_temp = os.path.join(temppath, 'guide.xml')

def xml_start():
    copyright = '<?xml version="1.0" encoding="UTF-8" ?>\n<!-- EPG XMLTV FILE CREATED BY Take-a-LUG TEAM- (c) 2020 Bastian Kleinschmidt -->\n<!-- created on {} -->\n<tv>\n'.format(str(now))
    with open(guide_temp,'w', encoding='utf-8') as f:
        f.write(copyright)

def xml_channels_start(provider):
    start = '\n<!--  {}  CHANNEL LIST -->\n'.format(provider)
    with open(guide_temp,'a', encoding='utf-8') as f:
        f.write(start)

def xml_channels(channel_name, channel_id, channel_icon, lang):
    channels = []
    channels.append('<channel id="{}">\n'.format(channel_id))
    channels.append('  <display-name lang="{}">{}</display-name>\n'.format(lang,channel_name))
    channels.append('  <icon src="{}" />\n'.format(channel_icon))
    channels.append('</channel>\n')
    s = ''.join(channels).replace('&','&amp;')
    with open(guide_temp,'a', encoding='utf-8') as f:
        f.write(s)

def xml_broadcast_start(provider):
    start = '\n<!--  {}  PROGRAMME LIST -->'.format(provider)
    with open(guide_temp,'a', encoding='utf-8') as f:
        f.write(start)

def xml_broadcast(episode_format, channel_id, item_title, item_starttime, item_endtime, item_description, item_country, item_picture, item_subtitle, items_genre, item_date, item_season, item_episode, item_agerating, items_director, items_producer, items_actor, enable_rating_mapper, lang):
    guide = []
    guide.append('\n')
    
    ## Programme Condition
    if (not item_starttime == '' and not item_endtime == ''):
        guide.append('<programme start="{} +0000" stop="{} +0000" channel="{}">\n'.format(item_starttime,item_endtime,channel_id))
    
    ## IMAGE Condition
    if not item_picture == '':
        guide.append('  <icon src="{}"/>\n'.format(item_picture))
    
    ## TITLE Condition
    if not item_title == '':
        guide.append('  <title lang="{}">{}</title>\n'.format(lang,item_title))
    
    ## SUBTITLE Condition
    if not item_subtitle == '':
        guide.append('  <sub-title lang="{}">{}</sub-title>\n'.format(lang,item_subtitle))
    
    ## DESCRIPTION Condition
    if not item_description == '':
        if enable_rating_mapper == False:
            guide.append('  <desc lang="{}">{}</desc>\n'.format(lang,item_description))

        ## Rating Mapper
        elif enable_rating_mapper == True:
            if (not item_date == '' and not item_country == '' and not item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">({}) {} • S{} E{} • FSK {}\n{}</desc>\n'.format(lang,item_country,item_date,item_season,item_episode,item_agerating,item_description))
            elif (not item_date == '' and not item_country == '' and not item_agerating == ''  and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) {} • S{} • FSK {}\n{}</desc>\n'.format(lang,item_country,item_date,item_season,item_agerating,item_description))
            elif (not item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">({}) {} • E{} • FSK {}\n{}</desc>\n'.format(lang,item_country,item_date,item_episode,item_agerating,item_description))
            elif (not item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) {} • FSK {}\n{}</desc>\n'.format(lang,item_country,item_date,item_agerating,item_description))
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">({}) {} • S{} E{}\n{}</desc>\n'.format(lang,item_country,item_date,item_season,item_episode,item_description))
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) {} • S{}\n{}</desc>\n'.format(lang,item_country,item_date,item_season,item_description))
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">({}) {} • E{}\n{}</desc>\n'.format(lang,item_country,item_date,item_episode,item_description))
            elif (not item_date == '' and not item_country == '' and item_agerating == '' and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) {}\n{}</desc>\n'.format(lang,item_country,item_date,item_description))

            elif (item_date == '' and not item_country == '' and not item_agerating == '' and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">({}) • S{} E{} • FSK {}\n{}</desc>\n'.format(lang,item_country,item_season,item_episode,item_agerating,item_description))
            elif (item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">({}) • E{} • FSK {}\n{}</desc>\n'.format(lang,item_country,item_episode,item_agerating,item_description))
            elif (item_date == '' and not item_country == '' and not item_agerating == '' and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) • S{} • FSK {}\n{}</desc>\n'.format(lang,item_country,item_season,item_agerating,item_description))
            elif (item_date == '' and not item_country == '' and not item_agerating == '' and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) • FSK {}\n{}</desc>\n'.format(lang,item_country,item_agerating,item_description))
            elif (item_date == '' and not item_country == '' and item_agerating == ''  and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) • S{}\n{}</desc>\n'.format(lang,item_country,item_season,item_description))
            elif (item_date == '' and not item_country == '' and item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">({}) • E{}\n{}</desc>\n'.format(lang,item_country,item_episode,item_description))
            elif (item_date == '' and not item_country == '' and not item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({}) • FSK{}\n{}</desc>\n'.format(lang,item_country,item_agerating,item_description))
            elif (item_date == '' and not item_country == '' and item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">({})\n{}</desc>\n'.format(lang,item_country,item_description))

            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">{} • S{} E{} • FSK {}\n{}</desc>\n'.format(lang,item_date,item_season,item_episode,item_agerating,item_description))
            elif (not item_date == '' and item_country == '' and item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">{} • S{} E{}\n{}</desc>\n'.format(lang,item_date,item_season,item_episode,item_description))
            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">{} • S{} • FSK {}\n{}</desc>\n'.format(lang,item_date,item_season,item_agerating,item_description))
            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">{} • E{} • FSK {}\n{}</desc>\n'.format(lang,item_date,item_episode,item_agerating,item_description))
            elif (not item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">{} • FSK {}\n{}</desc>\n'.format(lang,item_date,item_agerating,item_description))
            elif (not item_date == '' and item_country == '' and item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">{}\n{}</desc>\n'.format(lang,item_date,item_description))

            elif (item_date == '' and item_country == '' and not item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">S{} E{} • FSK {}\n{}</desc>\n'.format(lang,item_season,item_episode,item_agerating,item_description))
            elif (item_date == '' and item_country == '' and item_agerating == ''  and not item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">S{} E{}\n{}</desc>\n'.format(lang,item_season,item_episode,item_description))
            elif (item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">S{} • FSK {}\n{}</desc>\n'.format(lang,item_season,item_agerating,item_description))
            elif (item_date == '' and item_country == '' and item_agerating == '' and not item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">S{}\n{}</desc>\n'.format(lang,item_season,item_description))

            elif (item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">E{} • FSK {}\n{}</desc>\n'.format(lang,item_episode,item_agerating,item_description))
            elif (item_date == '' and item_country == '' and item_agerating == ''  and item_season == '' and not item_episode == ''):
                guide.append('  <desc lang="{}">E{}\n{}</desc>\n'.format(lang,item_episode,item_description))
            elif (item_date == '' and item_country == '' and not item_agerating == ''  and item_season == '' and item_episode == ''):
                guide.append('  <desc lang="{}">FSK {}\n{}</desc>\n'.format(lang,item_agerating,item_description))

            else:
                guide.append('  <desc lang="{}">{}</desc>\n'.format(lang,item_description))

    ## GENRE Condition
    if not items_genre == '':
        genrelist = items_genre.split(',')
        for genre in genrelist:
            guide.append('  <category lang="{}">{}</category>\n'.format(lang,genre))
    
    ## DATE Condition
    if not item_date == '':
        guide.append('  <date>{}</date>\n'.format(item_date))
    
    ## COUNTRY Condition
    if not item_country == '':
        guide.append('  <country>{}</country>\n'.format(item_country))
    
    ## EPISODE Condition
    # XMLTV_NS
    if episode_format == 'xmltv_ns':
        if (not item_season == '' and not item_episode == ''):
            item_season_ns = int(item_season) - int(1)
            item_episode_ns = int(item_episode) - int(1)
            guide.append('  <episode-num system="xmltv_ns">{} . {} . </episode-num>\n'.format(str(item_season_ns),str(item_episode_ns)))
        elif (not item_season == '' and item_episode == ''):
            item_season_ns = int(item_season) - int(1)
            guide.append('  <episode-num system="xmltv_ns">{} . 0 . </episode-num>\n'.format(str(item_season_ns)))
        elif (item_season == '' and not item_episode == ''):
            item_episode_ns = int(item_episode) - int(1)
            guide.append('  <episode-num system="xmltv_ns">0 . {} . </episode-num>\n'.format(str(item_episode_ns)))
    # ONSCREEN
    elif episode_format == 'onscreen':
        if (not item_season == '' and not item_episode == ''):
            guide.append('  <episode-num system="onscreen">S{} E{}</episode-num>\n'.format(item_season,item_episode))
        elif (not item_season == '' and item_episode == ''):    
            guide.append('  <episode-num system="onscreen">S{}</episode-num>\n'.format(item_season))
        elif (item_season == '' and not item_episode == ''):
            guide.append('  <episode-num system="onscreen">E{}</episode-num>\n'.format(item_episode))
    
    ## AGE-RATING Condition
    if (not item_agerating == ''):
        guide.append('  <rating>\n')
        guide.append('      <value>{}</value>\n'.format(item_agerating))
        guide.append('  </rating>\n')
    
    ## CAST Condition
    producerlist = items_producer.split(',')
    directorlist = items_director.split(',')
    actorlist = items_actor.split(',')
    # Complete
    if (not items_director == '' and not items_producer == '' and not items_actor == ''):
        guide.append('  <credits>\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>\n'.format(producer))
        for director in directorlist:
            guide.append('      <director>{}</director>\n'.format(director))
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>\n'.format(actor))
        guide.append('  </credits>\n')
    # Producer + Director
    elif (not items_director == '' and not items_producer == '' and items_actor == ''):
        guide.append('  <credits>' + '\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>\n'.format(producer))
        for director in directorlist:
            guide.append('      <director>{}</director>\n'.format(director))
        guide.append('  </credits>\n')
    # Director + Actor
    elif (not items_director == '' and items_producer == '' and not items_actor == ''):
        guide.append('  <credits>\n')
        for director in directorlist:
            guide.append('      <director>{}</director>\n'.format(director))
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>\n'.format(actor))
        guide.append('  </credits>\n')
    # Producer + Actor
    elif (items_director == '' and not items_producer == '' and not items_actor == ''):
        guide.append('  <credits>\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>\n'.format(producer))
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>\n'.format(actor))
        guide.append('  </credits>\n')
    # Only Director
    elif (not items_director == '' and items_producer == '' and items_actor == ''):
        guide.append('  <credits>\n')
        for director in directorlist:
            guide.append('      <director>{}</director>\n'.format(director))
        guide.append('  </credits>\n')
    # Only Producer
    if (items_director == '' and not items_producer == '' and items_actor == ''):
        guide.append('  <credits>\n')
        for producer in producerlist:
            guide.append('      <producer>{}</producer>\n'.format(producer))
        guide.append('  </credits>\n')
    # Only Actor
    if (items_director == '' and items_producer == '' and not items_actor == ''):
        guide.append('  <credits>\n')
        for actor in actorlist:    
            guide.append('      <actor>{}</actor>\n'.format(actor))
        guide.append('  </credits>\n')
    
    guide.append('</programme>\n')
    s = ''.join(guide).replace('&','&amp;')
    with open(guide_temp,'a', encoding='utf-8') as f:
        f.write(s)

def xml_end():
    end = '\n</tv>\n'
    with open(guide_temp,'a' , encoding='utf-8') as f:
        f.write(end)

