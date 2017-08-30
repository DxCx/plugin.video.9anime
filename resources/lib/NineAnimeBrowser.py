import re
import urllib
from ui import utils
from ui import BrowserBase
from ui import http

class NineAnimeBrowser(BrowserBase.BrowserBase):
    _BASE_URL = "http://9anime.to"
    _ANIME_VIEW_ITEMS_RE = \
    re.compile("<div\sclass=\"item\">\s<a\shref=\".+?/watch/(.+?)\"\sclass=\"poster\"[^>]*?>\s<img\ssrc=\".+?url=([^\"]+?)\"\salt=\"(.+?)\">.*?</div>", re.DOTALL)
    _PAGES_RE = \
    re.compile("<div\sclass=\"paging\">\s(.+?)\s</div>", re.DOTALL)
    _PAGES_TOTAL_RE = \
    re.compile("<span\sclass=\"total\">(\d+)<\/span>", re.DOTALL)
    _GENRES_BOX_RE = \
    re.compile("<a>Genre</a>\s<ul\sclass=\"sub\">(.+?)</ul>", re.DOTALL)
    _GENRE_LIST_RE = \
    re.compile("<li><a\shref=\"/genre\/(.+?)\"\stitle=\"(.+?)\">",
               re.DOTALL)
    _EPISODES_RE = \
    re.compile("<li>\s<a.+?data-id=\"(.+?)\" data-base=\"(\d+)\".+?data-title=\"(.+?)\".+?href=\"\/watch\/.+?\">.+?</li>",
               re.DOTALL)
    _EPISODE_BOXES_RE = \
    re.compile("<i\sclass=\"fa\sfa-server\"></i>\s(.+?)\s</label>\s<div.+?>(.+?)</div>",
               re.DOTALL)

    _EPISODE_LINK_RE = re.compile("<li><div><a\shref=\"/([-\w\s\d]+?)/(\d+?)\"\sclass=\"anm_det_pop\"><strong>(.+?)</strong></a><i\sclass=\"anititle\">(.+?)</i>", re.DOTALL)

    def _get_by_filter(self, filterName, filterData, page=1):
        data = dict(filterData)
        data['page'] = page
        url = self._to_url("filter")
        return self._process_anime_view(url, data, "%s/%%d" % filterName, page)

    def _parse_anime_view(self, res):
        name = res[2]
        image = res[1]
        url = res[0]
        return utils.allocate_item(name, "animes/" + url, True, image)

    def _handle_paging(self, results, base_url, page):
        pages_html = self._PAGES_RE.findall(results)
        # No Pages? empty list ;)
        if not len(pages_html):
            return []

        total_pages = int(self._PAGES_TOTAL_RE.findall(pages_html[0])[0])
        if page >= total_pages:
            return [] # Last page

        next_page = page + 1
        name = "Next Page (%d/%d)" % (next_page, total_pages)
        return [utils.allocate_item(name, base_url % next_page, True, None)]

    def _process_anime_view(self, url, data, base_plugin_url, page):
        results = self._get_request(url, data)
        all_results = map(self._parse_anime_view,
                          self._ANIME_VIEW_ITEMS_RE.findall(results))
        all_results += self._handle_paging(results, base_plugin_url, page)
        return all_results

    def _format_episode(self, anime_url):
        def f(einfo):
            return {
                "id": int(einfo[1]),
                "url": "play/" + anime_url + "/" + einfo[1],
                "source": self._to_url("watch/%s/%s" % (anime_url, einfo[0])),
                "name": "Episode %s (%s)" % (einfo[1], einfo[2])
            }
        return f

    def _get_anime_info(self, anime_url):
        resp = self._get_request(self._to_url("/watch/%s" % anime_url))
        # Strip the server into boxes
        episodes_boxes = self._EPISODE_BOXES_RE.findall(resp)
        servers = [(i[0], self._EPISODES_RE.findall(i[1])) for i in episodes_boxes]
        servers = dict([(i[0], map(self._format_episode(anime_url),
                                   i[1][::-1])) for i in servers])
        return servers

    def search_site(self, search_string, page=1):
        data = {
            "keyword": search_string,
            "page": page,
        }
        url = self._to_url("search")
        return self._process_anime_view(url, data, "search/%s/%%d" % search_string, page)

    def get_recent_dubbed(self,  page=1):
        return self._get_by_filter('recent_dubbed', {
            "language" : "dubbed",
            "sort" : "episode_last_added_at:desc",
            "status[]" : "airing"
        }, page);

    def get_recent_subbed(self,  page=1):
        return self._get_by_filter('recent_subbed', {
            "language" : "subbed",
            "sort" : "episode_last_added_at:desc",
            "status[]" : "airing"
        }, page);

    def get_popular_dubbed(self,  page=1):
        return self._get_by_filter('popular_dubbed', {
            "language" : "dubbed",
            "sort" : "views:desc"
        }, page);

    def get_popular_subbed(self,  page=1):
        return self._get_by_filter('popular_subbed', {
            "language" : "subbed",
            "sort" : "views:desc"
        }, page);

    def get_latest(self, page=1):
        data = {
            "page": page,
        }
        url = self._to_url("updated")
        return self._process_anime_view(url, data, "latest/%d", page)

    def get_newest(self, page=1):
        data = {
            "page": page,
        }
        url = self._to_url("newest")
        return self._process_anime_view(url, data, "newest/%d", page)

    def get_genres(self):
        res = self._get_request(self._to_url("/watch"))
        genres_box = self._GENRES_BOX_RE.findall(res)[0]
        generes = self._GENRE_LIST_RE.findall(genres_box)
        generes_out = [(i[1], "genre/%s/1" % i[0]) for i in generes]
        return map(lambda x: utils.allocate_item(x[0], x[1], True, ''), generes_out)

    def get_genre(self, name, page=1):
        data = {
            "page": page,
        }
        url = self._to_url("genre/%s" % name)
        return self._process_anime_view(url, data, "genre/%s/%%d" % name, page)

    def get_anime_episodes(self, anime_url, returnDirectory=False):
        servers = self._get_anime_info(anime_url)
        mostSources = max(servers.iteritems(), key=lambda x: len(x[1]))[0]
        server = servers[mostSources]
        return map(lambda x: utils.allocate_item(x['name'], x['url'], returnDirectory, ''), server)

    def get_episode_sources(self, anime_url, episode):
        servers = self._get_anime_info(anime_url)
        # server list to server -> source
        sources = map(lambda x: (x[0], filter(lambda y: y['id'] == episode,x[1])), servers.iteritems())
        sources = filter(lambda x: len(x[1]) != 0, sources)
        sources = map(lambda x: (x[0], x[1][0]['source']), sources)
        return sources
