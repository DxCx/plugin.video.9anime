from resources.lib.ui import control
from resources.lib.ui import utils
from resources.lib.ui.SourcesList import SourcesList
from resources.lib.ui.router import on_param, route, router_process
from resources.lib.NineAnimeBrowser import NineAnimeBrowser
import urlparse

AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z")+1)]
MENU_ITEMS = [
    (control.lang(30009), "watchlist", True),
    (control.lang(30000), "latest", False),
    (control.lang(30001), "newest", False),
    (control.lang(30002), "recent_subbed", False),
    (control.lang(30003), "popular_subbed", False),
    (control.lang(30004), "recent_dubbed", False),
    (control.lang(30005), "popular_dubbed", False),
    (control.lang(30006), "genres", False),
    (control.lang(30007), "search_history", False),
    (control.lang(30008), "settings", False),
    (control.lang(30010), "logout", True),
]
SERVER_CHOICES = {
    "serverstreamango": "Streamango",
    "serverrapid": "RapidVideo",
    "servermycloud": "MyCloud",
    "serveropenload": "OpenLoad",
}

WATCHLIST_ITEMS = [
    (control.lang(30300), "watchlist_all"),
    (control.lang(30301), "watchlist_watching"),
    (control.lang(30302), "watchlist_completed"),
    (control.lang(30303), "watchlist_onhold"),
    (control.lang(30304), "watchlist_dropped"),
    (control.lang(30305), "watchlist_planned")
]

HISTORY_DELIM = ":_:"

_BROWSER = NineAnimeBrowser()
control.setContent('tvshows');

def isDirectoryStyle():
    style = control.getSetting('displaystyle')
    return "Directory" == style

def sortResultsByRes(fetched_urls):
    prefereResSetting = utils.parse_resolution_of_source(control.getSetting('prefres'))

    filtered_urls = filter(lambda x: utils.parse_resolution_of_source(x[0]) <=
                           prefereResSetting, fetched_urls)

    return sorted(filtered_urls, key=lambda x:
                  utils.parse_resolution_of_source(x[0]),
                  reverse=True)

def bookmark_cm(u):
    if not _BROWSER.is_logged_in():
        return []

    sysaddon = sys.argv[0]

    add_to = control.lang(40000)
    return [
        (add_to + control.lang(30301),
         'RunPlugin(%s?action=bookmark&anime_id=%s&folder=watching)' %
         (sysaddon, u)),
        (add_to + control.lang(30302),
         'RunPlugin(%s?action=bookmark&anime_id=%s&folder=watched)' %
         (sysaddon, u)),
        (add_to + control.lang(30303),
         'RunPlugin(%s?action=bookmark&anime_id=%s&folder=onhold)' %
         (sysaddon, u)),
        (add_to + control.lang(30304),
         'RunPlugin(%s?action=bookmark&anime_id=%s&folder=dropped)' %
         (sysaddon, u)),
        (add_to + control.lang(30305),
         'RunPlugin(%s?action=bookmark&anime_id=%s&folder=planned)' %
         (sysaddon, u)),
    ]

def unbookmark_cm(u):
    if not _BROWSER.is_logged_in():
        return []

    sysaddon = sys.argv[0]
    return [
        (control.lang(40001),
         'RunPlugin(%s?action=bookmark&anime_id=%s&folder=remove)' % (sysaddon,
                                                                      u)),
    ]

@on_param('action', 'bookmark')
def BOOKMARK_ACTION(payload, params):
    _BROWSER.bookmark(params['anime_id'], params['folder'])

    # removing an entry, we need to refersh
    if params['folder'] == 'remove':
        control.refresh()

@route('login')
def LOGIN(payload, params):
    _BROWSER.login()

@route('logout')
def LOGOUT(payload, params):
    _BROWSER.logout()

@route('login_refresh')
def LOGIN_REFRESH(payload, params):
    _BROWSER.login_refresh()

@route('settings')
def SETTINGS(payload, params):
    return control.settingsMenu();

@route('animes/*')
def ANIMES_PAGE(animeurl, params):
    order = control.getSetting('reverseorder')
    episodes = _BROWSER.get_anime_episodes(animeurl, isDirectoryStyle())
    if ( "Ascending" in order ):
        episodes = reversed(episodes)
    return control.draw_items(episodes)

@route('newest')
def NEWEST(payload, params):
    return control.draw_items(_BROWSER.get_newest(), bookmark_cm)

@route('newest/*')
def NEWEST_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_newest(int(payload)), bookmark_cm)

@route('latest')
def LATEST(payload, params):
    return control.draw_items(_BROWSER.get_latest(), bookmark_cm)

@route('latest/*')
def LATEST_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_latest(int(payload)), bookmark_cm)

@route('recent_subbed')
def SUBBED(payload, params):
    return control.draw_items(_BROWSER.get_recent_subbed(), bookmark_cm)

@route('recent_subbed/*')
def SUBBED_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_recent_subbed(int(payload)), bookmark_cm)

@route('recent_dubbed')
def DUBBED(payload, params):
    return control.draw_items(_BROWSER.get_recent_dubbed(), bookmark_cm)

@route('recent_dubbed/*')
def DUBBED_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_recent_dubbed(int(payload)), bookmark_cm)

@route('popular_subbed')
def POPSUBBED(payload, params):
    return control.draw_items(_BROWSER.get_popular_subbed(), bookmark_cm)

@route('popular_subbed/*')
def POPSUBBED_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_popular_subbed(int(payload)), bookmark_cm)

@route('popular_dubbed')
def POPDUBBED(payload, params):
    return control.draw_items(_BROWSER.get_popular_dubbed(), bookmark_cm)

@route('popular_dubbed/*')
def POPDUBBED_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_popular_dubbed(int(payload)), bookmark_cm)

@route('watchlist')
def WATCHLIST_PAGE(payload, params):
    return control.draw_items([utils.allocate_item(name, url, True, '') for name, url in WATCHLIST_ITEMS])

@route('watchlist_all')
def ALL(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_all(), unbookmark_cm)

@route('watchlist_all/*')
def ALL_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_all(int(payload)), unbookmark_cm)

@route('watchlist_watching')
def WATCHING(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_watching(), unbookmark_cm)

@route('watchlist_watching/*')
def WATCHING_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_watching(int(payload)), unbookmark_cm)

@route('watchlist_completed')
def WATCHED(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_completed(), unbookmark_cm)

@route('watchlist_completed/*')
def WATCHED_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_completed(int(payload)), unbookmark_cm)

@route('watchlist_onhold')
def ONHOLD(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_onhold(), unbookmark_cm)

@route('watchlist_onhold/*')
def ONHOLD_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_onhold(int(payload)), unbookmark_cm)

@route('watchlist_dropped')
def DROPPED(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_dropped(), unbookmark_cm)

@route('watchlist_dropped/*')
def DROPPED_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_dropped(int(payload)), unbookmark_cm)

@route('watchlist_planned')
def PLANNED(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_planned(), unbookmark_cm)

@route('watchlist_planned/*')
def PLANNED_PAGES(payload, params):
    return control.draw_items(_BROWSER.get_watchlist_planned(int(payload)), unbookmark_cm)

@route('search_history')
def SEARCH_HISTORY(payload, params):
    history = control.getSetting("9anime.history")
    history_array = history.split(HISTORY_DELIM)
    if history != "" and "Yes" in control.getSetting('searchhistory') :
        return control.draw_items(_BROWSER.search_history(history_array))
    else :
        return SEARCH(payload,params)

@route('clear_history')
def CLEAR_HISTORY(payload, params):
    control.setSetting("9anime.history","")
    return LIST_MENU(payload, params)

@route('search')
def SEARCH(payload, params):
    query = control.keyboard(control.lang(30007))
    if query:
        if "Yes" in control.getSetting('searchhistory') :
            history = control.getSetting("9anime.history")
            if history != "" :
                query = query+HISTORY_DELIM
            history=query+history
            while history.count(HISTORY_DELIM) > 6 :
                history=history.rsplit(HISTORY_DELIM, 1)[0]
            control.setSetting("9anime.history",history)
        return control.draw_items(_BROWSER.search_site(query))
    return False

@route('search/*')
def SEARCH_PAGES(payload, params):
    query, page = payload.rsplit("/", 1)
    return control.draw_items(_BROWSER.search_site(query,
                                                   int(page)),
                              bookmark_cm)

@route('genres')
def LIST_GENRES(payload, params):
    return control.draw_items(_BROWSER.get_genres())

@route('genre/*')
def GENRE_ANIMES(payload, params):
    genre, page = payload.rsplit("/", 1)
    return control.draw_items(_BROWSER.get_genre(genre, int(page)), bookmark_cm)

@route('play/*')
def PLAY(payload, params):
    anime_url, episode = payload.rsplit("/", 1)
    sources = _BROWSER.get_episode_sources(anime_url, int(episode))

    serverChoice = filter(lambda x:
        control.getSetting(x[0]) == 'true', SERVER_CHOICES.iteritems())
    serverChoice = map(lambda x: x[1], serverChoice)
    sources = filter(lambda x: x[0] in serverChoice, sources)

    autoplay = True if 'true' in control.getSetting('autoplay') else False

    s = SourcesList(sources, autoplay, sortResultsByRes, {
        'title': control.lang(30100),
        'processing': control.lang(30101),
        'choose': control.lang(30102),
        'notfound': control.lang(30103),
    })

    if isDirectoryStyle():
        if s._read_sources():
            items = sorted(s._sources.iteritems(), key=lambda x: x[0])
            items = [(title[5:], url) for title, url in items]
            items = map(lambda x: utils.allocate_item(x[0], 'playlink&url=/'+x[1],'', False, ''), items)
            return control.draw_items(items)
    else:
        return control.play_source(s.get_video_link())

@route('playlink*')
def PLAY_SOURCE(payload, params):
    return control.play_source(urlparse.unquote(payload))

@route('')
def LIST_MENU(payload, params):
    is_logged_in = _BROWSER.is_logged_in()
    menu_items = filter(lambda x: not x[2] or is_logged_in, MENU_ITEMS)

    return control.draw_items([utils.allocate_item(name, url, True, '') for name, url, logged_only in menu_items])

router_process(control.get_plugin_url(), control.get_plugin_params())
