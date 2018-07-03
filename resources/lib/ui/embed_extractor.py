import re
import urllib
import urlparse
import utils
import http
import json
import time

from NineAnimeUrlExtender import NineAnimeUrlExtender
_EMBED_EXTRACTORS = {}

_9ANIME_EXTRA_PARAM = 674

def set_9anime_extra(new_val):
    global _9ANIME_EXTRA_PARAM
    _9ANIME_EXTRA_PARAM = new_val

def load_video_from_url(in_url):
    found_extractor = None

    for extractor in _EMBED_EXTRACTORS.keys():
        if in_url.startswith(extractor):
            found_extractor = _EMBED_EXTRACTORS[extractor]
            break

    if found_extractor is None:
        print "[*E*] No extractor found for %s" % in_url
        return None

    try:
        if found_extractor['preloader'] is not None:
            print "Modifying Url: %s" % in_url
            in_url = found_extractor['preloader'](in_url)

        print "Probing source: %s" % in_url
        reqObj = http.send_request(in_url)
        return found_extractor['parser'](http.raw_url(reqObj.url),
                                         reqObj.text,
                                         http.get_referer(in_url))
    except http.URLError:
        return None # Dead link, Skip result
    except:
        raise

    return None

def __set_flash(url):
    def f(req):
        req.add_header('X-Requested-With', 'ShockwaveFlash/19.0.0.226')
        return req
    return f

def __check_video_list(refer_url, vidlist, add_referer=False,
                       ignore_cookie=False):
    nlist = []
    for item in vidlist:
        try:
            item_url = item[1]
            if add_referer:
                item_url = http.add_referer_url(item_url, refer_url)

            temp_req = http.head_request(item_url)
            if temp_req.status_code != 200:
                print "[*] Skiping Invalid Url: %s - status = %d" % (item[1],
                                                             temp_req.status_code)
                continue # Skip Item.

            out_url = temp_req.url
            if ignore_cookie:
                out_url = http.strip_cookie_url(out_url)

            nlist.append((item[0], out_url))
        except Exception, e:
            # Just don't add source.
            pass

    return nlist

def __9anime_extract_direct(refer_url, grabInfo):
    # grabInfo['grabber'] sometimes ands with /?server=23 so we have to concat with & instead of ?
    url_parameter_concat = "&" if "?" in grabInfo['grabber'] else "?"
    url = "%s%s%s" % (grabInfo['grabber'], url_parameter_concat, urllib.urlencode(grabInfo['params']))
    url = __relative_url(refer_url, url)
    resp = json.loads(http.send_request(http.add_referer_url(url, refer_url)).text)

    possible_error = resp['error'] if 'error' in resp.keys() else 'No-Error-Set'
    if 'data' not in resp.keys():
        if possible_error == 'deleted':
            return None
        raise Exception('Failed to parse 9anime direct with error: %s' %
                        resp['error'] if 'error' in resp.keys() else
                        'No-Error-Set')

    if 'error' in resp.keys() and resp['error']:
        print '[*E*] Failed to parse 9anime direct but got data with error: %s' % resp['error']

    return __check_video_list(refer_url, map(lambda x: (x['label'], x['file']), resp['data']))

def __final_resolve_rapidvideo(url, label, referer=None):
    VIDEO_RE = re.compile("\<source\ssrc=\"([^\"]+?)\"")
    VIDEO_RE_NEW = re.compile(",\ssrc: \"([^\"]+?)\"")
    raw_url = "%s&q=%s" % (url, label)

    def playSource():
        reqObj = http.send_request(http.add_referer_url(raw_url, referer))
        if reqObj.status_code != 200:
            raise Exception("Error from server %d" % reqObj.status_code)

        results = VIDEO_RE.findall(reqObj.text)
        if not results:
            results = VIDEO_RE_NEW.findall(reqObj.text)
        if not results:
            raise Exception("Unable to find source")

        return results[0]

    return playSource

def __extract_streamango(url, page_content, referer=None):
    url = __extract_with_urlresolver(url, page_content, referer)()
    res = url.rsplit('|')[0].rsplit('/', 1)[-1]
    return [(res, url)]

def __extract_rapidvideo(url, page_content, referer=None):
    SOURCES_RE = re.compile("\<a\shref=\".+q=(.+?)\"\>")
    source_labels = SOURCES_RE.findall(page_content)
    sources = [
        (label, __final_resolve_rapidvideo(url, label, referer))
        for label in source_labels]

    return sources

def __9anime_retry(ep_id, server_id, retry):
    reqUrl = "https://projectman.ga/api/url?id=%s&server=%s&retry=%s" % \
    (ep_id, server_id, retry)
    response = json.loads(http.send_request(reqUrl).text)
    result_url = response["results"]

    # Store for next
    try:
        url_info = urlparse.urlparse(result_url)
        arguments = dict(urlparse.parse_qsl(url_info.query))
        set_9anime_extra(arguments["_"])
    except:
        print "[*E*] retry store failed"

    return result_url

def __extract_9anime(url, page_content, referer=None):
    episode_id = url.rsplit('/', 1)[1]
    url_info = urlparse.urlparse(url)
    domain = url_info.netloc
    scheme = url_info.scheme

    url_base = "%s://%s" % (scheme, domain)

    server_id = NineAnimeUrlExtender.get_server_value(page_content)
    ts_value = NineAnimeUrlExtender.get_ts_value(page_content)
    #extra_param = NineAnimeUrlExtender.get_extra_url_parameter(episode_id, server_id, ts_value)
    extra_param = _9ANIME_EXTRA_PARAM

    tryNo = 0
    ep_info_url = "%s/ajax/episode/info?ts=%s&_=%s&id=%s&server=%d" % \
    (url_base, ts_value, extra_param, episode_id, server_id)

    while True:
        time.sleep(0.3)
        urlRequest = http.send_request(ep_info_url)
        grabInfo = json.loads(urlRequest.text)
        grabInfo = NineAnimeUrlExtender.decode_info(grabInfo)
        if 'error' in grabInfo.keys():
            if tryNo < 2:
                tryNo += 1
                retry = "true" if tryNo == 2 else "false"
                ep_info_url = __9anime_retry(episode_id, server_id, retry)
                continue

            raise Exception('error while trying to fetch info: %s' %
                            grabInfo['error'])

        break

    if grabInfo['type'] == 'iframe':
        target = grabInfo['target']
        if target.startswith('//'):
            target = "%s:%s" % (url_info.scheme, target)

        return load_video_from_url(http.add_referer_url(target, url))
    elif grabInfo['type'] == 'direct':
        return __9anime_extract_direct(url, grabInfo)

    raise Exception('Unknown case, please report')

def __animeram_factory(in_url, page_content, referer=None):
    IFRAME_RE = re.compile("<iframe.+?src=\"(.+?)\"")
    embeded_url = IFRAME_RE.findall(page_content)[0]
    embeded_url = __relative_url(in_url, embeded_url)
    return load_video_from_url(embeded_url)

def __extract_js_var(content, name):
    value_re = re.compile("%s=\"(.+?)\";" % name, re.DOTALL)
    deref_re = re.compile("%s=(.+?);" % name, re.DOTALL)
    value = value_re.findall(content)
    if len(value):
        return value[0]

    deref = deref_re.findall(content)
    if not len(deref):
        return "undefined"
    return __extract_js_var(content, deref[0])

def __extract_swf_player(url, content, referer=None):
    domain = __extract_js_var(content, "flashvars\.domain")
    assert domain is not "undefined"

    key = __extract_js_var(content, "flashvars\.filekey")
    filename = __extract_js_var(content, "flashvars\.file")
    cid, cid2, cid3 = ("undefined", "undefined", "undefined")
    user, password = ("undefined", "undefined")

    data = {
            'key': key,
            'file': filename,
            'cid': cid,
            'cid2': cid2,
            'cid3': cid3,
            'pass': password,
            'user': user,
            'numOfErrors': "0"
    }
    token_url = "%s/api/player.api.php?%s" % (domain, urllib.urlencode(data))

    video_info_res = http.send_request(http.add_referer_url(token_url, url), set_request=__set_flash(url))
    video_info = dict(urlparse.parse_qsl(video_info_res.text))

    if video_info.has_key("error_msg"):
        print "[*] Error Message: %s" % (video_info["error_msg"])
    if not video_info.has_key("url"):
        return None
    return video_info['url']

def __extract_with_urlresolver(url, content, referer=None):
    # NOTE: Requires urlresolver dependancy (script.module.urlresolver) in
    # addon.xml

    import urlresolver
    return lambda: urlresolver.resolve(url)

def __extract_mycloud(url, content, referer=None):
    fixHttp = lambda x: ("https://" + x) if not x.startswith("http") else x
    strip_res = lambda x: x.split("/")[-1].split(".")[0]
    formatUrls = lambda x: (strip_res(x), http.add_referer_url(x, url))

    # Get m3u of all res
    m3u_list = re.findall("\"file\"\s*:\s*\"\/*(.+)\"", content)
    m3u_list = map(fixHttp, m3u_list)
    m3u_list = m3u_list[0]

    # Read and parse all res
    playlist_req = http.send_request(http.add_referer_url(m3u_list, url))
    if playlist_req.status_code != 200:
        raise Exception("Error from server %d" % playlist_req.status_code)

    playlist_content = playlist_req.text
    playlist_content = map(lambda x: x.strip(), playlist_content.split("\n"))
    playlist_content = filter(lambda x: not x.startswith("#") and len(x), playlist_content)

    # Build source urls
    sources = map(lambda x: __relative_url(m3u_list, x), playlist_content)
    sources = map(formatUrls, sources)

    return __check_video_list(url, sources, True, True)

# Thanks to https://github.com/munix/codingground
def __extract_openload(url, content):
    splice = lambda s, start, end: s[:start] + s[start + end:]

    ol_id = re.findall('<span[^>]+id=\"[^\"]+\"[^>]*>([0-9a-z]+)</span>', content)[0]
    arrow = ord(ol_id[0])
    pos = arrow - 52
    nextOpen = max(2, pos)
    pos = min(nextOpen, len(ol_id) - 30 - 2)
    part = ol_id[pos: pos + 30]
    arr = [0] * 10
    i = 0
    while i < len(part):
      arr[i / 3] = int(part[i: i + 3], 8)
      i += 3

    chars = [i for i in ol_id]
    chars = splice(chars, pos, 30)

    a = ''.join(chars)
    tagNameArr = []
    i = 0
    n = 0
    while i < len(a):
      text = a[i: i + 2]
      cDigit = a[i: i + 3]
      ch = a[i: i + 4]
      code = int(text, 16)
      i += 2
      if n % 3 is 0:
        code = int(cDigit, 8)
        i += 1
      else:
        if n % 2 is 0:
          if 0 is not n:
            if ord(a[n - 1][0]) < 60:
              code = int(ch, 10)
              i += 2

      val = arr[n % 9]
      code ^= 213
      code ^= val
      tagNameArr.append(chr(code))
      n += 1

    video_url = "https://openload.co/stream/" + ''.join(tagNameArr) + "?mime=true"
    return http.head_request(video_url).url

def __register_extractor(urls, function, url_preloader=None):
    if type(urls) is not list:
        urls = [urls]

    for url in urls:
        _EMBED_EXTRACTORS[url] = {
            "preloader": url_preloader,
            "parser": function,
        }

def __ignore_extractor(url, content, referer=None):
    return None

def __relative_url(original_url, new_url):
    if new_url.startswith("http://") or new_url.startswith("https://"):
        return new_url

    if new_url.startswith("//"):
        return "http:%s" % new_url
    else:
        return urlparse.urljoin(original_url, new_url)

def __extractor_factory(regex, double_ref=False, match=0, debug=False):
    compiled_regex = re.compile(regex, re.DOTALL)

    def f(url, content, referer=None):
        if debug:
            print url
            print content
            print compiled_regex.findall(content)
            raise

        try:
            regex_url = compiled_regex.findall(content)[match]
            regex_url = __relative_url(url, regex_url)
            if double_ref:
                video_url = utils.head_request(http.add_referer_url(regex_url, url)).url
            else:
                video_url = __relative_url(regex_url, regex_url)
            return video_url
        except Exception, e:
            print "[*E*] Failed to load link: %s: %s" % (url, e)
            return None
    return f

__register_extractor([
    "https://9anime.to/watch/",
    "https://9anime.tv/watch/",
    "https://9anime.is/watch/",

    "http://9anime.to/watch/",
    "http://9anime.tv/watch/",
    "http://9anime.is/watch/",
], __extract_9anime)

__register_extractor("http://ww1.animeram.cc", __animeram_factory)

__register_extractor("http://auengine.com/",
                    __extractor_factory("var\svideo_link\s=\s'(.+?)';"))

__register_extractor(["http://mp4upload.com/",
                      "http://www.mp4upload.com/",
                      "https://www.mp4upload.com/",
                      "https://mp4upload.com/"],
                    __extractor_factory("\"file\":\s\"(.+?)\","))

__register_extractor("http://videonest.net/",
                    __extractor_factory("\[\{file:\"(.+?)\"\}\],"))

__register_extractor(["http://animebam.com/", "http://www.animebam.net/"],
                    __extractor_factory("var\svideoSources\s=\s\[\{file:\s\"(.+?)\",", True))

__register_extractor(["http://yourupload.com/", "http://www.yourupload.com/", "http://embed.yourupload.com/"],
                     __extractor_factory("file:\s'(.+?\.mp4.*?)',", True))

__register_extractor("http://embed.videoweed.es/", __extract_swf_player)

__register_extractor("http://embed.novamov.com/", __extract_swf_player)

__register_extractor("https://openload.co/embed/", __extract_with_urlresolver)

__register_extractor(["https://mcloud.to/embed",
                      "https://mycloud.to/embed",
                      "http://mycloud.to/embed"],
                     __extract_mycloud)

__register_extractor(["https://www.rapidvideo.com/e/"],
                     __extract_rapidvideo)

__register_extractor(["https://streamango.com/embed/"],
                     __extract_streamango)

# TODO: debug to find how to extract
__register_extractor("http://www.animeram.tv/files/ads/160.html", __ignore_extractor)
