from resources.lib.ui import control
from resources.lib.ui import utils
from resources.lib.ui.SourcesList import SourcesList
from resources.lib.ui.router import route, router_process
from resources.lib.NineAnimeBrowser import NineAnimeBrowser

AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z")+1)]
MENU_ITEMS = [
    (control.lang(30000), "latest"),
    (control.lang(30001), "newest"),
    (control.lang(30002), "genres"),
    (control.lang(30003), "search")
]

@route('animes/*')
def ANIMES_PAGE(animeurl):
    return control.draw_items(NineAnimeBrowser().get_anime_episodes(animeurl))

@route('newest')
def NEWEST(payload):
    return control.draw_items(NineAnimeBrowser().get_newest())

@route('newest/*')
def NEWEST_PAGES(payload):
    return control.draw_items(NineAnimeBrowser().get_newest(int(payload)))

@route('latest')
def LATEST(payload):
    return control.draw_items(NineAnimeBrowser().get_latest())

@route('latest/*')
def LATEST_PAGES(payload):
    return control.draw_items(NineAnimeBrowser().get_latest(int(payload)))

@route('search')
def SEARCH(payload):
    query = control.keyboard(control.lang(30002))
    if query:
        return control.draw_items(NineAnimeBrowser().search_site(query))
    return False

@route('search/*')
def SEARCH_PAGES(payload):
    query, page = payload.rsplit("/", 1)
    return control.draw_items(NineAnimeBrowser().search_site(query,
                                                            int(page)))

@route('genres')
def LIST_GENRES(payload):
    return control.draw_items(NineAnimeBrowser().get_genres())

@route('genre/*')
def GENRE_ANIMES(payload):
    genre, page = payload.rsplit("/", 1)
    return control.draw_items(NineAnimeBrowser().get_genre(genre, int(page)))

@route('play/*')
def PLAY(payload):
    anime_url, episode = payload.rsplit("/", 1)
    s = SourcesList(NineAnimeBrowser().get_episode_sources(anime_url,
                                                           int(episode)), {
                        'title': control.lang(30100),
                        'processing': control.lang(30101),
                        'choose': control.lang(30102),
                        'notfound': control.lang(30103),
    })
    return control.play_source(s.get_video_link())

@route('')
def LIST_MENU(payload):
    return control.draw_items([utils.allocate_item(name, url, True) for name, url in MENU_ITEMS])

router_process(control.get_plugin_url())
