from . import embed_extractor

def allocate_item(name, url, is_dir=False, image=''):
    new_res = {}
    new_res['is_dir'] = is_dir
    new_res['image'] = image
    new_res['name'] = name
    new_res['url'] = url
    return new_res

def fetch_sources(sources, dialog, raise_exceptions=False):
    fetched_sources = []
    factor = 100.0 / len(sources)

    for i, do in enumerate(sources):
        if dialog.iscanceled():
            return None

        name, url = do
        try:
            dialog.update(int(i * factor), name)
            fetched_url = embed_extractor.load_video_from_url(url)
            if fetched_url is not None:
                fetched_sources.append(("%03d | %s" % (len(fetched_sources) + 1, name), fetched_url))
            else:
                print "Skipping invalid source %s" % name
            dialog.update(int(i * factor))
        except Exception, e:
            print "[*E*] Skiping %s because Exception at parsing" % name
            if raise_exceptions:
                raise
            else:
                print e

    if not len(fetched_sources):
        # No Valid sources found
        return None

    return dict(fetched_sources)
