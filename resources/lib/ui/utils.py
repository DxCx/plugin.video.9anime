from . import embed_extractor
from http import URLError, send_request, head_request
import re

_numbers_in_parentheses_regex = re.compile(ur'(\d+)\D*')

def allocate_item(name, url, is_dir=False, image='', plot=''):
    new_res = {}
    new_res['is_dir'] = is_dir
    new_res['image'] = image
    new_res['name'] = name
    new_res['url'] = url
    new_res['plot'] = plot
    return new_res

def parse_resolution_of_source(data):
    matches = _numbers_in_parentheses_regex.findall(data)
    if len(matches) == 0:
        return 0
    return int(matches[0])

def _format_source(i, item):
    label, fetched_url, name = item
    label = " (%s)" % label if len(label) else ''
    return ("%02d | %s%s" % (i, name, label), fetched_url)

def fetch_sources(sources, dialog, raise_exceptions=False, autoplay=False,
                  sortBy=None):
    # X[0] => Label, X[1] => Url, X[2] => Source
    total_urls = []
    factor = 100.0 / len(sources)

    for i, do in enumerate(sources):
        if dialog.iscanceled():
            return None

        name, url = do
        try:
            dialog.update(int(i * factor), name)
            fetched_urls = embed_extractor.load_video_from_url(url)
            if type(fetched_urls) is not list:
                fetched_urls = [('', fetched_urls)]

            # TODO: If first source doesn't contain perfered res,
            # Autoplay won't try to search for next source prefere
            # But use the first best source found.
            if autoplay and sortBy is not None:
                fetched_urls = sortBy(fetched_urls)
                item = fetched_urls[0]
                item = (item[0], item[1], name)
                if len(fetched_urls):
                    return dict([_format_source(0, item)])

            # X[0] => Label, X[1] => Url
            valid_urls = filter(lambda x: x[1] != None, fetched_urls)
            total_urls += map(lambda x: (x[0], x[1], name), valid_urls)
            dialog.update(int(i * factor))
        except Exception, e:
            print "[*E*] Skiping %s because Exception at parsing" % name
            if raise_exceptions:
                raise
            else:
                print e

    if sortBy is not None:
        total_urls = sortBy(total_urls)

    if not len(total_urls):
        # No Valid sources found
        return None

    fetched_sources = []
    for item in total_urls:
        fetched_sources.append(
            _format_source(len(fetched_sources) + 1, item)
        )

    return dict(fetched_sources)
