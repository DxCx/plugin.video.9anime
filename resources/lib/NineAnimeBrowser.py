import re
import urllib
from ui import utils
from ui import BrowserBase
from ui import http

class NineAnimeBrowser(BrowserBase.BrowserBase):
    _BASE_URL = "https://9anime.to"
    _ANIME_VIEW_ITEMS_RE = \
    re.compile("<div\sclass=\"item\">\s<a\shref=\"https://9anime.to/watch/(.+?)\"\sclass=\"poster\".*?>\s<img\ssrc=\".+?url=(.+?)\"\salt=\"(.+?)\">.*?</div>", re.DOTALL)
    _PAGES_RE = \
    re.compile("<div\sclass=\"paging\">\s(.+?)\s</div>", re.DOTALL)
    _PAGES_TOTAL_RE = \
    re.compile("<span\sclass=\"total\">(\d+)<\/span>", re.DOTALL)
    _GENRES_BOX_RE = \
    re.compile("<a>Genre</a>.+?<ul\sclass=\"sub\">(.+?)</ul>", re.DOTALL)
    _GENRE_LIST_RE = \
    re.compile("<li><a\shref=\".+?\/genre\/(.+?)\"\stitle=\"(.+?)\">.+?</li>",
               re.DOTALL)

    _EPISODE_LINK_RE = re.compile("<li><div><a\shref=\"/([-\w\s\d]+?)/(\d+?)\"\sclass=\"anm_det_pop\"><strong>(.+?)</strong></a><i\sclass=\"anititle\">(.+?)</i>", re.DOTALL)
    _ANIME_LIST_RESULTS_RE = re.compile("<li><a\shref=\"/([-\w\s\d]+?)\"\sclass=\"anm_det_pop\">(.+?)</a>", re.DOTALL)
    _NEWMANGA_CONT_RE = re.compile("<ul\sclass=\"newmanga\">(.+?)</ul>", re.DOTALL)

    _PLAYER_SOURCES_UL_RE = re.compile("<ul\sclass=\"nav\snav-tabs\">(.+?)</ul>", re.DOTALL)

    def _parse_search_result(self, res):
        name = res[2]
        image = res[1]
        url = res[0]
        return utils.allocate_item(name, "animes/" + url + "/", True, image)

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
        all_results = []
        for result in self._ANIME_VIEW_ITEMS_RE.findall(results):
            all_results.append(self._parse_search_result(result))

        all_results += self._handle_paging(results, base_plugin_url, page)
        return all_results

    def search_site(self, search_string, page=1):
        data = {
            "keyword": search_string,
            "page": page,
        }
        url = self._to_url("search")
        return self._process_anime_view(url, data, "search/%s/%%d" % search_string, page)

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
        res = self._get_request(self._to_url())
        genres_box = self._GENRES_BOX_RE.findall(res)[0]
        generes = self._GENRE_LIST_RE.findall(genres_box)
        generes = [(i[1], "genre/%s/1" % i[0]) for i in generes]
        return map(lambda x: utils.allocate_item(x[0], x[1], True, ''), generes)

    def get_genre(self, name, page=1):
        url = self._to_url("genre/%s" % name)
        return self._process_anime_view(url, None, "genre/%s/%%d" % name, page)

    def get_anime_episodes(self, anime_url):
        resp = self._get_request(self._to_url("/series/%s" % anime_url))
        resp = self._NEWMANGA_CONT_RE.findall(resp)[0]

        results = []
        for res in self._EPISODE_LINK_RE.findall(resp):
            ep_name = res[3].strip()
            if len(ep_name):
                name = "%s : %s" % (res[2] , ep_name)
            else:
                name = res[2]
            results.append(utils.allocate_item(name, "play/" + res[0] + "/" + res[1], False, ''))
        return results

    def get_episode_sources(self, episode_url):
        animeram_url = self._to_url(episode_url)
        resp = self._get_request(animeram_url)
        sources =  self._PLAYER_SOURCES_UL_RE.findall(resp)[0]
        link_regex = re.compile("<a href=\"(.+?)\">(.+?)<span>(.+?)</span></a>", re.DOTALL)
        tags_regex = re.compile("<span\sclass=\".+?\">(.+?)</span>")

        links = []
        for res in link_regex.findall(sources):
            tags = " ".join(["[%s]" % i for i in tags_regex.findall(res[1])])
            name = "%s %s" % (tags, res[-1])
            url = "%s/1" % episode_url if res[0] == "#"  else res[0]
            url = self._to_url(url)
            links.append((name, url))
        return links
