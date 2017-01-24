#!/usr/local/bin/python2
import unittest
import utils

TESTED_SOURCES = [
    ('[SUBBED] ABVideo', 'http://ww1.animeram.cc/naruto-shippuden/1/1'),
    ('[DUBBED] [HD] ABVideo', 'http://ww1.animeram.cc/naruto-shippuden/1/2'),
    ('[SUBBED] novamov', 'http://ww1.animeram.cc/naruto-shippuden/1/4'),
    ('[SUBBED] novamov', 'http://ww1.animeram.cc/naruto-shippuden/1/5'),
    ('[DUBBED] yourupload', 'http://ww1.animeram.cc/naruto-shippuden/1/10'),
    ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/11'),
    ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/13'),
    ('[SUBBED] videoweed', 'http://ww1.animeram.cc/naruto-shippuden/1/14'),
    ('[SUBBED] yourupload', 'http://ww1.animeram.cc/naruto-shippuden/1/15'),
    ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/16'),
    ('[SUBBED] videonest', 'http://ww1.animeram.cc/naruto-shippuden/1/17'),
    ('[SUBBED] mp4upload', 'http://ww1.animeram.cc/naruto-shippuden/1/18'),
    ('[DUBBED] novamov', 'http://ww1.animeram.cc/naruto-shippuden/1/19'),
    ('[DUBBED] novamov', 'http://ww1.animeram.cc/naruto-shippuden/1/20')
]

class MockedDialog(object):
    def __init__(self):
        pass

    def update(self, precentage, name=None):
        pass

    def iscanceled(self):
        return False

class TestUtils(unittest.TestCase):
    def test_fetch_sources(self):
        "fetch_sources fetches at least 50% of the sources"
        dialog = MockedDialog()
        fetched = utils.fetch_sources(TESTED_SOURCES, dialog, True)
        # Make sure we have at least 50% hit rate
        self.assertGreaterEqual(len(fetched), len(TESTED_SOURCES) / 2)

if __name__ == "__main__":
    unittest.main()
