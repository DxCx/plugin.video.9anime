import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

HANDLE=int(sys.argv[1])
ADDON_NAME = 'plugin.video.animeram'
__settings__ = xbmcaddon.Addon(ADDON_NAME)
__language__ = __settings__.getLocalizedString
CACHE = StorageServer.StorageServer("%s.animeinfo" % ADDON_NAME, 24)

def getSetting(key):
    return __settings__.getSetting(key)

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

def keyboard(text):
    keyboard = xbmc.Keyboard("", text, False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    return None

def xbmc_add_player_item(name, url, iconimage=''):
    ok=True
    u=addon_url(url)
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty("fanart_image", __settings__.getAddonInfo('path') + "/fanart.jpg")
    liz.setProperty("Video", "true")
    liz.setProperty("IsPlayable", "true")
    liz.addContextMenuItems([], replaceItems=False)
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz, isFolder=False)
    return ok

def xbmc_add_dir(name, url, iconimage=''):
    ok=True
    u=addon_url(url)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty("fanart_image", __settings__.getAddonInfo('path') + "/fanart.jpg")
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz,isFolder=True)
    return ok

def play_source(link):
    if link:
        xbmcplugin.setResolvedUrl(HANDLE, True, xbmcgui.ListItem(path=link))
    else:
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())

def draw_items(video_data):
    for vid in video_data:
        if vid['is_dir']:
            xbmc_add_dir(vid['name'], vid['url'], vid['image'])
        else:
            xbmc_add_player_item(vid['name'], vid['url'], vid['image'])
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)
    return True
