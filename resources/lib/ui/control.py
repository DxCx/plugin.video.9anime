import re
import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import http
import urlparse

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

HANDLE=int(sys.argv[1])
ADDON_NAME = re.findall('plugin:\/\/([\w\d\.]+)\/', sys.argv[0])[0]
__settings__ = xbmcaddon.Addon(ADDON_NAME)
__language__ = __settings__.getLocalizedString
CACHE = StorageServer.StorageServer("%s.animeinfo" % ADDON_NAME, 24)

def setContent(contentType):
    xbmcplugin.setContent(HANDLE, contentType)

def refresh():
    return xbmc.executebuiltin('Container.Refresh')

def settingsMenu():
    return xbmcaddon.Addon().openSettings()

def getSetting(key):
    return __settings__.getSetting(key)

def setSetting(id, value):
    return __settings__.setSetting(id=id, value=value)

def cache(funct, *args):
    return CACHE.cacheFunction(funct, *args)

def lang(x):
    return __language__(x).encode('utf-8')

def addon_url(url=''):
    return "plugin://%s/%s" % (ADDON_NAME, url)

def get_plugin_url():
    addon_base = addon_url()
    assert sys.argv[0].startswith(addon_base), "something bad happened in here"
    return sys.argv[0][len(addon_base):]

def get_plugin_params():
    return dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))

def keyboard(text):
    keyboard = xbmc.Keyboard("", text, False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    return None

def xbmc_add_player_item(name, url, iconimage='', description='', draw_cm=None):
    ok=True
    u=addon_url(url)
    cm = draw_cm(u) if draw_cm is not None else []

    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name, "Plot": description })
    liz.setProperty("fanart_image", __settings__.getAddonInfo('path') + "/fanart.jpg")
    liz.setProperty("Video", "true")
    liz.setProperty("IsPlayable", "true")
    liz.addContextMenuItems(cm, replaceItems=False)
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz, isFolder=False)
    return ok

def xbmc_add_dir(name, url, iconimage='', description='', draw_cm=None):
    ok=True
    u=addon_url(url)
    cm = draw_cm(u) if draw_cm is not None else []

    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name, "Plot": description })
    liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems(cm, replaceItems=False)
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz,isFolder=True)
    return ok

def _prefetch_play_link(link):
    if callable(link):
        link = link()

    if not link:
        return None

    linkInfo = http.head_request(link);
    if linkInfo.status_code != 200:
        raise Exception('could not resolve %s. status_code=%d' %
                        (link, linkInfo.status_code))
    return {
        "url": linkInfo.url,
        "headers": linkInfo.headers,
    }

def play_source(link):
    linkInfo = _prefetch_play_link(link)
    if not linkInfo:
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return

    item = xbmcgui.ListItem(path=linkInfo['url'])
    if 'Content-Type' in linkInfo['headers']:
        item.setProperty('mimetype', linkInfo['headers']['Content-Type'])

    xbmcplugin.setResolvedUrl(HANDLE, True, item)

def draw_items(video_data, draw_cm=None):
    for vid in video_data:
        if vid['is_dir']:
            xbmc_add_dir(vid['name'], vid['url'], vid['image'], vid['plot'], draw_cm)
        else:
            xbmc_add_player_item(vid['name'], vid['url'], vid['image'],
                                 vid['plot'], draw_cm)
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)
    return True
