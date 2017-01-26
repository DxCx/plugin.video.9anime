import re
import urllib
from ui import utils
from ui import BrowserBase
from ui import http

class NineAnimeBrowser(BrowserBase.BrowserBase):
    _BASE_URL = "https://9anime.to"
    _RELEVANT_RESULTS_RE = \
    re.compile("<div\sclass=\"item\">\s<a\shref=\"https://9anime.to/watch/(.+?)\"\sclass=\"poster\".*?>\s<img\ssrc=\".+?url=(.+?)\"\salt=\"(.+?)\">.*?</div>", re.DOTALL)
    _SEARCH_PAGES_RE = \
    re.compile("<div\sclass=\"paging\">\s(.+?)\s</div>", re.DOTALL)
    _SEARCH_PAGES_TOTAL_RE = \
    re.compile("<span\sclass=\"total\">(\d+)<\/span>", re.DOTALL)
    _LATEST_LINK_RE = re.compile("<li><div><span\sclass=\"rightside\">.+?<a\shref=\"/([-\w\s\d]+?)/(\d+?)/\w+\"\sclass=\"anm_det_pop\"><strong>(.+?)</strong>.+?</a>.+?<img\ssrc=\"(.+?)\">.+?</li>", re.DOTALL)
    _EPISODE_LINK_RE = re.compile("<li><div><a\shref=\"/([-\w\s\d]+?)/(\d+?)\"\sclass=\"anm_det_pop\"><strong>(.+?)</strong></a><i\sclass=\"anititle\">(.+?)</i>", re.DOTALL)
    _ANIME_LIST_RESULTS_RE = re.compile("<li><a\shref=\"/([-\w\s\d]+?)\"\sclass=\"anm_det_pop\">(.+?)</a>", re.DOTALL)
    _NEWMANGA_CONT_RE = re.compile("<ul\sclass=\"newmanga\">(.+?)</ul>", re.DOTALL)
    _INFO_IMG_RE = re.compile("<img class=\"cvr\" src=\"(.+?)\"", re.DOTALL)

    _PLAYER_SOURCES_UL_RE = re.compile("<ul\sclass=\"nav\snav-tabs\">(.+?)</ul>", re.DOTALL)

    def _parse_search_result(self, res):
        name = res[2]
        image = res[1]
        url = res[0]
        return utils.allocate_item(name, "animes/" + url + "/", True, image)

    def _handle_paging(self, results, base_url, page):
        pages_html = self._SEARCH_PAGES_RE.findall(results)
        # No Pages? empty list ;)
        if not len(pages_html):
            return []

        total_pages = int(self._SEARCH_PAGES_TOTAL_RE.findall(pages_html[0])[0])
        if page >= total_pages:
            return [] # Last page

        next_page = page + 1
        name = "Next Page (%d/%d)" % (next_page, total_pages)
        return [utils.allocate_item(name, base_url % next_page, True, None)]

    def search_site(self, search_string, page=1):
        url = self._to_url("search?%s" % urllib.urlencode({
            "keyword": search_string,
            "page": page,
        }))

        results = self._get_request(url)
        all_results = []
        for result in self._RELEVANT_RESULTS_RE.findall(results):
            all_results.append(self._parse_search_result(result))

        all_results += self._handle_paging(results, "search/%s/%%d" % search_string, page)
        return all_results

    def get_latest(self):
        resp = self._get_request(self._to_url())
        resp = self._NEWMANGA_CONT_RE.findall(resp)

        results = []
        for container in resp:
            for res in self._LATEST_LINK_RE.findall(container):
                image = "http:%s" % res[3]
                name = res[2]
                results.append(utils.allocate_item(name, "play/" + res[0] + "/" + res[1], False, image))
        return results

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

    def get_anime_list(self, letter):
        filter_regx = re.compile("<div\sid=\"nm%(ll)s\"\sname=\"nm%(ll)s\"\sclass=\"panel-body\">%(ul)s</div><div\sclass=\"panel-footer\"><ul\sclass=\"series_alpha\">(.+?)</ul>" % {"ul": letter.upper(), "ll": letter.lower()}, re.DOTALL)
        resp = self._get_request(self._to_url("series"))
        filtered = filter_regx.findall(resp)[0]

        results = []
        for res in self._ANIME_LIST_RESULTS_RE.findall(filtered):
            results.append(utils.allocate_item(res[1], "animes/%s/" % res[0], True, ''))
        return results
