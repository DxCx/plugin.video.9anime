from resources.lib.ui import control
from resources.lib.ui import utils
from resources.lib.ui.SourcesList import SourcesList
from resources.lib.ui.router import route, router_process
from resources.lib.NineAnimeBrowser import NineAnimeBrowser
import urlparse

AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z")+1)]
MENU_ITEMS = [
    (control.lang(30009), "watchlist"),
    (control.lang(30000), "latest"),
    (control.lang(30001), "newest"),
    (control.lang(30002), "recent_subbed"),
    (control.lang(30003), "popular_subbed"),
    (control.lang(30004), "recent_dubbed"),
    (control.lang(30005), "popular_dubbed"),
    (control.lang(30006), "genres"),
    (control.lang(30007), "search"),
    (control.lang(30008), "settings")
]
SERVER_CHOICES = {
    "serverstreamango": "Streamango",
    "serverrapid": "RapidVideo",
    "servermycloud": "MyCloud",
    "serveropenload": "OpenLoad",
}

WATCHLIST_ITEMS = [
    (control.lang(30010), "all"),
    (control.lang(30011), "watching"),
    (control.lang(30012), "completed"),
    (control.lang(30013), "onhold"),
    (control.lang(30014), "dropped"),
    (control.lang(30015), "planned")
]

_BROWSER = NineAnimeBrowser()
control.setContent('tvshows');

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))

try: action = params['action']
except: action = None

try: anime_id = params['anime_id']
except: anime_id = None

try: folder = params['folder']
except: folder = None

if action == 'bookmark':
    _BROWSER.bookmark(anime_id, folder)
    
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

@route('login')
def LOGIN(payload):
    _BROWSER.login()

@route('login_refresh')
def LOGIN_REFRESH(payload):
    _BROWSER.login_refresh()

@route('settings')
def SETTINGS(payload):
    return control.settingsMenu();

@route('animes/*')
def ANIMES_PAGE(animeurl):
    order = control.getSetting('reverseorder')
    episodes = _BROWSER.get_anime_episodes(animeurl, isDirectoryStyle())
    if ( "Ascending" in order ):
        episodes = reversed(episodes)
    return control.draw_items(episodes)

@route('watchlist')
def LOGIN_MENU(payload):
    return control.draw_items([utils.allocate_item(name, url, True, '') for name, url in WATCHLIST_ITEMS])

@route('newest')
def NEWEST(payload):
    return control.draw_items(_BROWSER.get_newest())

@route('newest/*')
def NEWEST_PAGES(payload):
    return control.draw_items(_BROWSER.get_newest(int(payload)))

@route('latest')
def LATEST(payload):
    return control.draw_items(_BROWSER.get_latest())

@route('latest/*')
def LATEST_PAGES(payload):
    return control.draw_items(_BROWSER.get_latest(int(payload)))

@route('recent_subbed')
def SUBBED(payload):
    return control.draw_items(_BROWSER.get_recent_subbed())

@route('recent_subbed/*')
def SUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_recent_subbed(int(payload)))

@route('recent_dubbed')
def DUBBED(payload):
    return control.draw_items(_BROWSER.get_recent_dubbed())

@route('recent_dubbed/*')
def DUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_recent_dubbed(int(payload)))

@route('popular_subbed')
def POPSUBBED(payload):
    return control.draw_items(_BROWSER.get_popular_subbed())

@route('popular_subbed/*')
def POPSUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_popular_subbed(int(payload)))

@route('popular_dubbed')
def POPDUBBED(payload):
    return control.draw_items(_BROWSER.get_popular_dubbed())

@route('popular_dubbed/*')
def POPDUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_popular_dubbed(int(payload)))

@route('all')
def ALL(payload):
    return control.draw_items(_BROWSER.get_all())

@route('all/*')
def ALL_PAGES(payload):
    return control.draw_items(_BROWSER.get_all(int(payload)))

@route('watching')
def WATCHING(payload):
    return control.draw_items(_BROWSER.get_watching())

@route('watching/*')
def WATCHING_PAGES(payload):
    return control.draw_items(_BROWSER.get_watching(int(payload)))

@route('completed')
def WATCHED(payload):
    return control.draw_items(_BROWSER.get_completed())

@route('completed/*')
def WATCHED_PAGES(payload):
    return control.draw_items(_BROWSER.get_completed(int(payload)))

@route('onhold')
def ONHOLD(payload):
    return control.draw_items(_BROWSER.get_onhold())

@route('onhold/*')
def ONHOLD_PAGES(payload):
    return control.draw_items(_BROWSER.get_onhold(int(payload)))

@route('dropped')
def DROPPED(payload):
    return control.draw_items(_BROWSER.get_dropped())

@route('dropped/*')
def DROPPED_PAGES(payload):
    return control.draw_items(_BROWSER.get_dropped(int(payload)))

@route('planned')
def PLANNED(payload):
    return control.draw_items(_BROWSER.get_planned())

@route('planned/*')
def PLANNED_PAGES(payload):
    return control.draw_items(_BROWSER.get_planned(int(payload)))

@route('search')
def SEARCH(payload):
    query = control.keyboard(control.lang(30007))
    if query:
        return control.draw_items(_BROWSER.search_site(query))
    return False

@route('search/*')
def SEARCH_PAGES(payload):
    query, page = payload.rsplit("/", 1)
    return control.draw_items(_BROWSER.search_site(query,
                                                            int(page)))

@route('genres')
def LIST_GENRES(payload):
    return control.draw_items(_BROWSER.get_genres())

@route('genre/*')
def GENRE_ANIMES(payload):
    genre, page = payload.rsplit("/", 1)
    return control.draw_items(_BROWSER.get_genre(genre, int(page)))

@route('play/*')
def PLAY(payload):
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
def PLAY_SOURCE(payload):
    return control.play_source(urlparse.unquote(payload))

@route('')
def LIST_MENU(payload):
    if control.getSetting("login.auth") == '':
        return control.draw_items([utils.allocate_item(name, url, True, '') for name, url in MENU_ITEMS[1:]])
    else:
        return control.draw_items([utils.allocate_item(name, url, True, '') for name, url in MENU_ITEMS])

router_process(control.get_plugin_url())
