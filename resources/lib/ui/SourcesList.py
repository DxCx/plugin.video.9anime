from utils import fetch_sources
from DialogProgressWrapper import DialogProgressWrapper
import re
import xbmcgui

class SourcesList(object):
    def __init__(self, raw_results, strings = None):
        self._raw_results = raw_results
        if not strings or not len(strings):
            strings = {
                'title': 'Fetching Sources',
                'processing': 'Processing %s',
                'choose': 'Please choose source: ',
                'notfound': 'Couldn\'t find eliable sources',
            }

        self._strings = strings
        self._sources = []

    def _fetch_sources(self, sources, dialog):
        fetched_sources = fetch_sources(sources, dialog)
        if not fetched_sources:
            return None

        self._sources = fetched_sources
        return True

    def _fetch_sources_progress(self, sources):
        dialog = DialogProgressWrapper(self._strings['title'],
                                       self._strings['processing'])
        ret = self._fetch_sources(sources, dialog)
        dialog.close()
        return ret

    def _read_sources(self):
        if not len(self._raw_results):
            # No Sources to start with
            return None

        return self._fetch_sources_progress(self._raw_results)

    def _select_source(self):
        if len(self._sources) == 1:
            print "1 source was found, returning it"
            return self._sources.values()[0]

        dialog = xbmcgui.Dialog()
        slist = sorted(self._sources.keys())
        sel = dialog.select(self._strings['choose'], slist)
        if sel == -1:
            return None
        return self._sources[slist[sel]]

    def get_video_link(self):
        if not self._read_sources():
            dialog = xbmcgui.Dialog()
            dialog.notification(self._strings['notfound'], "", xbmcgui.NOTIFICATION_ERROR)
            return None
        return self._select_source()

    @property
    def name(self):
        return self._name
