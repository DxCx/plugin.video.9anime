import re
import urllib2
import urllib
from ui import utils

class AnimeramBrowser(object):
    _BASE_URL = "http://ww1.animeram.cc"
    _RELEVANT_RESULTS_RE = re.compile("<a\shref=\"/series/(.+?)\"\sclass=\"mse\">(.+?)</a>", re.DOTALL)
    _SEARCH_IMAGE_RE = re.compile("<img\ssrc=\"(.+?)\"", re.DOTALL)
    _NAME_LINK_RE = re.compile("<h2>(.+?)</h2>", re.DOTALL)
    _LATEST_LINK_RE = re.compile("<li><div><span\sclass=\"rightside\">.+?<a\shref=\"/([-\w\s\d]+?)/(\d+?)/\w+\"\sclass=\"anm_det_pop\"><strong>(.+?)</strong>.+?</a>.+?<img\ssrc=\"(.+?)\">.+?</li>", re.DOTALL)
    _EPISODE_LINK_RE = re.compile("<li><div><a\shref=\"/([-\w\s\d]+?)/(\d+?)\"\sclass=\"anm_det_pop\"><strong>(.+?)</strong></a><i\sclass=\"anititle\">(.+?)</i>", re.DOTALL)
    _ANIME_LIST_RESULTS_RE = re.compile("<li><a\shref=\"/([-\w\s\d]+?)\"\sclass=\"anm_det_pop\">(.+?)</a>", re.DOTALL)
    _NEWMANGA_CONT_RE = re.compile("<ul\sclass=\"newmanga\">(.+?)</ul>", re.DOTALL)
    _INFO_IMG_RE = re.compile("<img class=\"cvr\" src=\"(.+?)\"", re.DOTALL)

    _PLAYER_SOURCES_UL_RE = re.compile("<ul\sclass=\"nav\snav-tabs\">(.+?)</ul>", re.DOTALL)

    def __init__(self):
        pass

    def _to_url(self, url=''):
        if url.startswith("/"):
            url = url[1:]
        return "%s/%s" % (self._BASE_URL, url)

    def _post_request(self, url, data={}):
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')
        response = urllib2.urlopen(req)
        response_content = response.read()
        response.close()
        return response_content

    def _get_request(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')
        response = urllib2.urlopen(req)
        resp = response.read()
        response.close()
        return resp

    def _parse_search_result(self, res):
        name = self._NAME_LINK_RE.findall(res[1])[0]
        image = "http:%s" % self._SEARCH_IMAGE_RE.findall(res[1])[0]
        url = res[0]
        return utils.allocate_item(name, "animes/" + url + "/", True, image)

    def search_site(self, search_string):
        url = self._to_url("search?%s" % urllib.urlencode({"search": search_string}))
        results = self._get_request(url)
        all_results = []
        for result in self._RELEVANT_RESULTS_RE.findall(results):
            all_results.append(self._parse_search_result(result))
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
