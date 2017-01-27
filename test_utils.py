#!/usr/local/bin/python2
import unittest
import utils

class MockedDialog(object):
    def __init__(self):
        pass

    def update(self, precentage, name=None):
        pass

    def iscanceled(self):
        return False

class TestUtils(unittest.TestCase):

    def _test_sources(self, sources):
        fetched = utils.fetch_sources(sources, MockedDialog(), True)
        # Make sure we have at least 50% hit rate
        self.assertIsNotNone(fetched)
        self.assertGreaterEqual(len(fetched), len(sources) / 2)
        return fetched

    def test_fetch_nineanime_openload(self):
        "fetch_sources fetches 9anime (OpenLoad)"
        self._test_sources([
            (u'OpenLoad', u'https://9anime.to/watch/one-piece.ov8/7jqp66'),
            (u'OpenLoad', u'https://9anime.to/watch/one-piece.ov8/xry4kz'),
            (u'OpenLoad', u'https://9anime.to/watch/one-piece.ov8/1nkj0x'),
        ])

    def test_fetch_nineanime_direct(self):
        "fetch_sources fetches 9anime (Direct)"
        self._test_sources([
            (u'Server F1', u'https://9anime.to/watch/one-piece.ov8/6lpo5p'),
            (u'Server F2', u'https://9anime.to/watch/one-piece.ov8/52on4q')
        ])

    def test_fetch_abvideo(self):
        "fetch_sources fetches ABVideo"
        self._test_sources([
            ('[SUBBED] ABVideo', 'http://ww1.animeram.cc/one-piece/773/1'),
            ('[SUBBED] ABVideo', 'http://ww1.animeram.cc/naruto-shippuden/1/1'),
            ('[DUBBED] [HD] ABVideo', 'http://ww1.animeram.cc/naruto-shippuden/1/2'),
        ])

    def test_fetch_yourupload(self):
        "fetch_sources fetches yourupload"
        self._test_sources([
            ('[DUBBED] yourupload', 'http://ww1.animeram.cc/naruto-shippuden/1/10'),
            ('[SUBBED] yourupload', 'http://ww1.animeram.cc/naruto-shippuden/1/15'),
        ])

    def test_fetch_novamov(self):
        "fetch_sources fetches novamov"
        self._test_sources([
            ('[SUBBED] novamov', 'http://ww1.animeram.cc/naruto-shippuden/1/5'),
            ('[DUBBED] novamov', 'http://ww1.animeram.cc/naruto-shippuden/1/19'),
            ('[DUBBED] novamov', 'http://ww1.animeram.cc/naruto-shippuden/1/20')
        ])

    def test_fetch_mp4upload(self):
        "fetch_sources fetches novamov"
        self._test_sources([
            ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/11'),
            ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/13'),
            ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/16'),
            ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/18'),
        ])

    def test_fetch_others(self):
        "fetch_sources fetches others less common providers"
        self._test_sources([
            ('[SUBBED] videoweed', 'http://ww1.animeram.cc/naruto-shippuden/1/14'),
            ('[SUBBED] videonest', 'http://ww1.animeram.cc/naruto-shippuden/1/17'),
        ])

if __name__ == "__main__":
    unittest.main()
