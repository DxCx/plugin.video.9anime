import re
import urllib
from ui import utils
from ui import BrowserBase
from ui import http
from ui import control
import json,xbmcgui,xbmcaddon,requests,xbmc,bs4 as bs

from ui.embed_extractor import set_9anime_extra
set_9anime_extra(744)
SERVERS_TOKEN = 648

class NineAnimeBrowser(BrowserBase.BrowserBase):
    _BASE_URL = "https://9anime.to"
    _ANIME_VIEW_ITEMS_RE = \
    re.compile("<div\sclass=\"item\">\s<div\sclass=\"inner\">\s<a\shref=\".+?/watch/(.+?)\"\s[^>]+?>\s<img\ssrc=\"(.+?)\"\salt=\"([^\"]+?)\"[^>]*?>.+?<\/div>\s<\/div>", re.DOTALL)
    _ANIME_WATCHLIST_VIEW_ITEMS_RE = \
    re.compile('<div class="item .+?"> <a class="thumb" href="/watch/(.+?)"><img alt="(.+?)" src="(.+?)"/></a>', re.DOTALL)
    _PAGES_RE = \
    re.compile("<div\sclass=\"paging-wrapper\">\s(.+?)\s</div>", re.DOTALL)
    _PAGES_TOTAL_RE = \
    re.compile("<span\sclass=\"total\">(\d+)<\/span>", re.DOTALL)
    _PAGES_WATCHLIST_TOTAL_RE = \
    re.compile('.+?-page=(.+?)', re.DOTALL)
    _GENRES_BOX_RE = \
    re.compile("<a>Genre</a>\s<ul\sclass=\"sub\">(.+?)</ul>", re.DOTALL)
    _GENRE_LIST_RE = \
    re.compile("<li>\s<a\shref=\"/genre\/(.+?)\"\stitle=\"(.+?)\">",
               re.DOTALL)
    _EPISODES_RE = \
    re.compile("<li>\s<a.+?data-id=\"(.+?)\" data-base=\"(\d+)\".+?data-comment=\"(.+?)\".+?data-title=\"(.+?)\".+?href=\"\/watch\/.+?\">(.+?)</a>\s</li>",
               re.DOTALL)
    _PLOT_RE = \
    re.compile('<div class="desc">(.+?)</div>', re.DOTALL)
    _EPISODE_IMAGE_RE = \
    re.compile('<div class="thumb col-md-5 hidden-sm hidden-xs"> <img src="(.+?)\"', re.DOTALL)
    _EPISODE_PANEL_RE = \
    re.compile("\<div\sclass=\"widget\sservers\"\>\s(.+)\<\/div\>", re.DOTALL)
    _EPISODE_PANEL_POST_RE = \
    re.compile("\<div\sclass=\"widget-title\"\>\s+?(.+)\s+?\<\/div\>\s+?\<div\sclass=\"widget-body\"\>\s+?(.+)\s+?\<\/div\>", re.DOTALL)
    _SERVER_NAMES_RE = \
    re.compile("\<span\sclass=\"tab\s\w*\"\sdata-name=\"(\d+)\">([^<]+?)</span>",
               re.DOTALL)

    def _get_by_filter(self, filterName, filterData, page=1):
        data = dict(filterData)
        data['page'] = page
        url = self._to_url("filter")
        return self._process_anime_view(url, data, "%s/%%d" % filterName, page)

    def _get_watchlist_request(self, url, data=None):
        cookie = {'__cfduid': '%s' %(control.getSetting("login.tokencfd")),'web_theme': 'dark', 'session': '%s' %(control.getSetting("login.tokenses")), 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': '%s' %(control.getSetting("login.tokenrem"))}
        results = requests.get(url, data, cookies=cookie)
        if results.status_code == 200:
            pass
        elif results.status_code == 503:
            xbmc.executebuiltin('RunPlugin(plugin://plugin.video.9anime/login_refresh)')
            cookie = {'__cfduid': '%s' %(control.getSetting("login.tokencfd")),'web_theme': 'dark', 'session': '%s' %(control.getSetting("login.tokenses")), 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': '%s' %(control.getSetting("login.tokenrem"))}
            results = requests.get(url, data, cookies=cookie)
        results = results.text
        soup = bs.BeautifulSoup(results, 'html.parser')
        results = soup.find_all('div', attrs={"class":"content "})
        return results

    def _parse_anime_view(self, res):
        name = res[2]
        image = res[1]
        url = res[0]
        return utils.allocate_item(name, "animes/" + url, True, image)

    def _parse_history_view(self, res):
        name = res
        return utils.allocate_item(name, "search/" + name + "/1", True)

    def _parse_watchlist_anime_view(self, res):
        name = res[1]
        image = res[2]
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

    def _handle_watchlist_paging(self, results, base_url, page):
        pages_html = self._PAGES_WATCHLIST_TOTAL_RE.findall(str(results))
        # No Pages? empty list ;)
        if not len(pages_html):
            return []

        total_pages = int(self._PAGES_WATCHLIST_TOTAL_RE.findall(str(results))[-2])
        if page >= total_pages:
            return [] # Last page

        next_page = page + 1
        name = "Next Page (%d/%d)" % (next_page, total_pages)
        return [utils.allocate_item(name, base_url % next_page, True, None)]

    def _get_anime_plot(self, url):
        resp = self._get_request(self._to_url("/watch/%s" % url))
        return self._extract_anime_extra(resp)['plot']

    def _extract_anime_extra(self, resp):
        replot = self._PLOT_RE.findall(resp)
        reimage = self._EPISODE_IMAGE_RE.findall(resp)
        plot = ''.join(replot)
        return {
            "plot": plot,
            "image": reimage[0],
        }

    def _process_anime_view(self, url, data, base_plugin_url, page):
        results = self._get_request(url, data)
        all_results = map(self._parse_anime_view,
                          self._ANIME_VIEW_ITEMS_RE.findall(results))
        all_results += self._handle_paging(results, base_plugin_url, page)
        return all_results

    def _process_watchlist_view(self, url, data, base_plugin_url, page):
        results = self._get_watchlist_request(url, data)
        all_results = map(self._parse_watchlist_anime_view,
                          self._ANIME_WATCHLIST_VIEW_ITEMS_RE.findall(str(results)))
        all_results += self._handle_watchlist_paging(results, base_plugin_url, page)
        return all_results

    def _format_episode(self, anime_url, extra, server_id):
        def f(einfo):
            source = self._to_url("watch/%s/%s?server_id=%s" % (anime_url,
                                                                einfo.attrs["data-id"],
                                                                server_id))
            base = {}
            base.update(extra)
            base.update({
                "id": einfo.attrs["data-comment"],
                "url": "play/" + anime_url + "/" + einfo.attrs["data-comment"],
                "source": source,
                "name": "Episode %s" % (einfo.string)
            })
            return base

        return f

    def _url_to_film(self, anime_url):
        anime_code = anime_url.split(".")[-1]
        return self._to_url("/ajax/film/servers/%s?_=%d" %
                            (anime_code, SERVERS_TOKEN))

    def _get_anime_info(self, anime_url):
        resp = self._get_request(self._to_url("/watch/%s" % anime_url))
        extra_data = self._extract_anime_extra(resp)

        servers_url = self._url_to_film(anime_url)
        resp = json.loads(self._get_request(servers_url))["html"]

        # Strip the server into boxes
        episodes_panel = self._EPISODE_PANEL_RE.findall(resp)[0]
        servers_text, epi_text = self._EPISODE_PANEL_POST_RE.findall(episodes_panel)[0]
        snames = dict(self._SERVER_NAMES_RE.findall(servers_text))

        # TODO: Try and soup above as well.
        soup = bs.BeautifulSoup(epi_text, 'html.parser')
        episodes_boxes = soup.find_all('div', attrs={"class":
                         lambda x: x and x.startswith("server ")})

        servers = [(snames[i.attrs["data-id"]],
                   i.attrs["data-id"], i.find_all('a')) for i in episodes_boxes]

        servers = dict([(i[0],
                         map(self._format_episode(anime_url, extra_data, i[1]),
                             i[2][::-1]))
                        for i in servers])
        return servers

    def search_site(self, search_string, page=1):
        data = {
            "keyword": search_string,
            "page": page,
        }
        url = self._to_url("search")
        return self._process_anime_view(url, data, "search/%s/%%d" % search_string, page)

    def search_history(self,search_array):
    	result = map(self._parse_history_view,search_array)
    	result.insert(0,utils.allocate_item("New Search", "search", True))
    	result.insert(len(result),utils.allocate_item("Clear..", "clear_history", True))
    	return result

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

    def get_watchlist_all(self, page=1):
        data = {
            "folder": 'all',
            "all-page": page
            }
        url = self._to_url("user/watchlist")
        return self._process_watchlist_view(url, data, "watchlist_all/%d", page)

    def get_watchlist_watching(self,  page=1):
        data = {
            "folder": 'watching',
            "watching-page": page
            }
        url = self._to_url("user/watchlist")
        return self._process_watchlist_view(url, data, "watchlist_watching/%d", page)

    def get_watchlist_completed(self,  page=1):
        data = {
            "folder": 'watched',
            "watched-page": page
            }
        url = self._to_url("user/watchlist")
        return self._process_watchlist_view(url, data, "watchlist_completed/%d", page)

    def get_watchlist_onhold(self,  page=1):
        data = {
            "folder": 'onhold',
            "onhold-page": page
            }
        url = self._to_url("user/watchlist")
        return self._process_watchlist_view(url, data, "watchlist_onhold/%d", page)

    def get_watchlist_dropped(self,  page=1):
        data = {
            "folder": 'dropped',
            "dropped-page": page
            }
        url = self._to_url("user/watchlist")
        return self._process_watchlist_view(url, data, "watchlist_dropped/%d", page)

    def get_watchlist_planned(self,  page=1):
        data = {
            "folder": 'planned',
            "planned-page": page
            }
        url = self._to_url("user/watchlist")
        return self._process_watchlist_view(url, data, "watchlist_planned/%d", page)

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
        if not servers: return []
        mostSources = max(servers.iteritems(), key=lambda x: len(x[1]))[0]
        server = servers[mostSources]
        return map(lambda x: utils.allocate_item(x['name'],
                                                 x['url'],
                                                 returnDirectory,
                                                 x['image'],
                                                 x['plot']), server)

    def get_episode_sources(self, anime_url, episode):
        servers = self._get_anime_info(anime_url)
        if not servers: return []
        # server list to server -> source
        sources = map(lambda x: (x[0], filter(lambda y: y['id'] == episode,x[1])), servers.iteritems())
        sources = filter(lambda x: len(x[1]) != 0, sources)
        sources = map(lambda x: (x[0], x[1][0]['source']), sources)
        return sources

    def _to_url_login(self, url):
        return self._to_url(url).replace('https://', 'https://%s.' % (control.getSetting("9anime.login_tld")))

    def is_logged_in(self):
        return control.getSetting("login.auth") != ''

    def logout(self):
        control.setSetting(id='login.tokenrem', value='')
        control.setSetting(id='login.tokenses', value='')
        control.setSetting(id='login.tokencfd', value='')
        control.setSetting(id='login.auth', value='')
        control.refresh()

    def login(self):
        try:
            control.setSetting(id='login.tokenrem', value='')
            control.setSetting(id='login.tokenses', value='')
            control.setSetting(id='login.tokencfd', value='')
            payload = {
                'username': control.getSetting("9anime.username"),
                'password': control.getSetting("9anime.password"),
                'remember': 1
                }
            url = self._to_url_login("user/ajax/login")
            p = requests.post(url, data=payload)
            r = p.headers['Set-Cookie']
            remember_me = ''.join(re.compile('remember_web_.+?=(.+?);').findall(r))
            session = ''.join(re.compile('session=(.+?);').findall(r))
            cfduid = ''.join(re.compile('__cfduid=(.+?);').findall(r))
            control.setSetting(id='login.tokenrem', value=remember_me)
            control.setSetting(id='login.tokenses', value=session)
            control.setSetting(id='login.tokencfd', value=cfduid)
            control.setSetting(id='login.auth', value='loggedin')
            dialog = xbmcgui.Dialog()
            dialog.ok(control.lang(30200), json.loads(p.text)['message'])
            control.refresh()
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok(control.lang(30200), control.lang(30201))

    def login_refresh(self):
        try:
            control.setSetting(id='login.tokenrem', value='')
            control.setSetting(id='login.tokenses', value='')
            control.setSetting(id='login.tokencfd', value='')
            payload = {
                'username': control.getSetting("9anime.username"),
                'password': control.getSetting("9anime.password"),
                'remember': 1
                }
            url = self._to_url_login("user/ajax/login")
            p = requests.post(url, data=payload)
            r = p.headers['Set-Cookie']
            remember_me = ''.join(re.compile('remember_web_.+?=(.+?);').findall(r))
            session = ''.join(re.compile('session=(.+?);').findall(r))
            cfduid = ''.join(re.compile('__cfduid=(.+?);').findall(r))
            control.setSetting(id='login.tokenrem', value=remember_me)
            control.setSetting(id='login.tokenses', value=session)
            control.setSetting(id='login.tokencfd', value=cfduid)
            control.setSetting(id='login.auth', value='loggedin')
            dialog = xbmcgui.Dialog()
            dialog.ok(control.lang(30200), control.lang(30202))
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok(control.lang(30200), control.lang(30201))

    def bookmark(self, anime_id, folder):
        anime_id = anime_id.split('.')[-1]
        data = {
            "id" : anime_id[:4],
            "folder": folder,
            "random": 1
            }
        cookie = {'__cfduid': '%s' %(control.getSetting("login.tokencfd")),'web_theme': 'dark', 'session': '%s' %(control.getSetting("login.tokenses")), 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': '%s' %(control.getSetting("login.tokenrem"))}
        url = self._to_url_login("user/ajax/edit-watchlist")
        results = requests.get(url, data, cookies=cookie)
        if results.status_code == 200:
            pass
        elif results.status_code == 503:
            xbmc.executebuiltin('RunPlugin(plugin://plugin.video.9anime/login_refresh)')
            cookie = {'__cfduid': '%s' %(control.getSetting("login.tokencfd")),'web_theme': 'dark', 'session': '%s' %(control.getSetting("login.tokenses")), 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': '%s' %(control.getSetting("login.tokenrem"))}
            results = requests.get(url, data, cookies=cookie)
        dialog = xbmcgui.Dialog()
        dialog.ok(control.lang(30203), json.loads(results.text)['message'])

    def episode_playing(self, anime_id):
        try:
            anime_id = ' '.join(anime_id)
            anime_id = anime_id.rsplit('.', 1)[-1]
            anime_id = anime_id.rsplit('/', 1)
            data = {
                'data[%s]' %(anime_id[0]): anime_id[1]
                }
            cookie = {'__cfduid': '%s' %(control.getSetting("login.tokencfd")),'web_theme': 'dark', 'session': '%s' %(control.getSetting("login.tokenses")), 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': '%s' %(control.getSetting("login.tokenrem"))}
            url = self._to_url_login("user/ajax/playing")
            results = requests.post(url, data, cookies=cookie)
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok(control.lang(30203), control.lang(30204))
