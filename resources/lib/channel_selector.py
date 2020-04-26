# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import json
import os

ADDON = xbmcaddon.Addon(id="service.takealug.epg-grabber")
addon_name = ADDON.getAddonInfo('name')
addon_version = ADDON.getAddonInfo('version')
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
temppath = os.path.join(datapath, "temp")

# Make a debug logger
def log(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log('[{} {}] {}'.format(addon_name, addon_version, message), loglevel)

# Make OSD Notify Messages
OSD = xbmcgui.Dialog()

def notify(title, message, icon=xbmcgui.NOTIFICATION_INFO):
    OSD.notification(title, message, icon)

def select_channels(provider,online_list,user_list):
    """
    Shows a multiselect list
    :param online_list: channellist of provider
    :type online_list: JSON (dict)
    :param user_list: channellist of user
    :type user_list; JSON (dict)
    :return: JSON of new user_list if success, None if aborted
    """

    items = list()
    selected = list()
    index = 0
    for channel in online_list.get('channellist', []):
        descriptor = xbmcgui.ListItem(label=channel['name'])
        descriptor.setArt({'icon': channel['pictures'][0]['href']})
        descriptor.setProperty({'item': json.dumps(channel)})
        for user_item in user_list.get('channellist', []):
            if channel['contentId'] == user_item['contentId']:
                # mark as 'selected', write mandantory index
                selected.append(index)
                if channel['name'] != user_item['name']:
                    # mark as 'channelname has changed' (label2)
                    descriptor.setLabel2(user_item['name'])
            break
        items.append(descriptor)
        index += 1
    # check for outdated channels in user list
    for user_item in user_list.get('channellist', []):
        if user_item['contentId'] not in online_list.get('channellist', [])['contentId']:
            xbmc.log('content id {} is outdated'.format(user_item['contentId']))
    # build new userlist
    multilist = xbmcgui.Dialog().multiselect('Channels from Provider', items, preselect=selected, useDetails=True)
    if multilist is not None:
        user_list = list()
        for selected in multilist:
            user_list.append(json.loads(items[selected].getProperty('item')))
        return dict({'channellist': user_list})
    xbmc.log('selection of channela aborted')
    return None