#!/usr/local/bin/python2
import time
import unittest
import utils

from NineAnimeTokenDecoder import NineAnimeTokenDecoder
from http import send_request

class MockRequest(object):
    def __init__(self):
        self._cookies = {}

    def add_cookie(self, key, value):
        self._cookies.update({ key: value })

    @property
    def cookies(self):
        return self._cookies.keys()

class TestUtils(unittest.TestCase):
    def _sleep(self):
        time.sleep(1)

    def test_token_decode(self):
        text1 = '(+((!+[]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(+!![]+[])+(!+[]+!![]+[])))>>(!+[]+!![]+!![]+!![]+!![]+!![]+!![])'
        text2 = '((+((+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+[])))-(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]))/(!+[]+!![]+!![])'
        result1 = NineAnimeTokenDecoder._decode_as_int(text1)
        result2 = NineAnimeTokenDecoder._decode_as_int(text2)
        self.assertEquals(54, result1)
        self.assertEquals(49, result2)
        self._sleep()

    def test_set_request(self):
        set_request = NineAnimeTokenDecoder.set_request('https://9anime.is/token?v1', send_request)
        r = set_request(MockRequest())
        self.assertGreater(len(r.cookies), 0)
        self._sleep()

if __name__ == "__main__":
    unittest.main()
