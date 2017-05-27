#!/usr/local/bin/python2
import time
import unittest

from resources.lib.NineAnimeBrowser import NineAnimeBrowser

__all__ = [ "TestBrowser" ]

class TestBrowser(unittest.TestCase):
    def __init__(self, *args, **kargs):
        super(TestBrowser, self).__init__(*args, **kargs)
        self.browser = NineAnimeBrowser()

    def _sleep(self):
        time.sleep(1)

    def test_search_site(self):
        "search site finds naruto"
        search_res = self.browser.search_site("Naruto Shippuden")
        self.assertGreater(len(search_res), 0)

        search_item = filter(lambda x: x['name'] == 'Naruto: Shippuuden (Dub)', search_res)
        self.assertEquals(len(search_item), 1)
        self.assertEquals(search_item[0]['url'], 'animes/naruto-shippuuden-dub.00zr')
        self.assertEquals(search_item[0]['is_dir'], True)
        self._sleep()

    def test_search_with_pages(self):
        "search 'Dragon' and verify pages"
        search_res = self.browser.search_site("Dragon")
        self.assertGreaterEqual(len(search_res), 30)
        self.assertEqual(search_res[-1]['name'].startswith('Next Page (2'), True)
        self.assertEqual(search_res[-1], {
            'name': search_res[-1]['name'],
            'is_dir': True,
            'image': None,
            'url': 'search/Dragon/2'
        })
        self._sleep()

    def test_get_latest(self):
        "get_latest returns at least 10 items"
        latest = self.browser.get_latest()
        self.assertGreater(len(latest), 10)
        self._sleep()

    def test_get_latest_pages(self):
        "get_latest returns next page"
        latest = self.browser.get_latest()
        self.assertEqual(latest[-1]['name'].startswith('Next Page (2'), True)
        self.assertEqual(latest[-1], {
            'name': latest[-1]['name'],
            'is_dir': True,
            'image': None,
            'url': 'latest/2'
        })
        self._sleep()

    def test_get_newest(self):
        "get_newest returns at least 10 items"
        newest = self.browser.get_newest()
        self.assertGreater(len(newest), 10)
        self._sleep()

    def test_get_newest_pages(self):
        "get_newest returns next page"
        newest = self.browser.get_newest()
        self.assertEqual(newest[-1]['name'].startswith('Next Page (2'), True)
        self.assertEqual(newest[-1], {
            'name': newest[-1]['name'],
            'is_dir': True,
            'image': None,
            'url': 'newest/2'
        })
        self._sleep()

    def test_get_genres(self):
        "get_genres returns genere list"
        genre_list = self.browser.get_genres()
        self.assertGreater(len(genre_list), 0)
        self.assertIn({
            'url': 'genre/comedy/1',
            'is_dir': True,
            'image': '',
            'name': 'Comedy'
        }, genre_list)
        self._sleep()

    def test_get_genre(self):
        "get_genre returns anime list by genre"
        anime_list = self.browser.get_genre("action")
        self.assertGreater(len(anime_list), 10)
        self._sleep()

    def test_get_genre_pages(self):
        "get_genre returns anime list with pages"
        anime_list = self.browser.get_genre("action", 1)
        self.assertEqual(anime_list[-1]['name'].startswith('Next Page (2'), True)
        self.assertEqual(anime_list[-1], {
            'name': anime_list[-1]['name'],
            'is_dir': True,
            'image': None,
            'url': 'genre/action/2'
        })
        self._sleep()

    def test_get_anime_episodes(self):
        "get_anime_episodes works for one-piece"
        episodes = self.browser.get_anime_episodes("one-piece.ov8")
        self.assertGreaterEqual(len(episodes), 750)
        self.assertEqual(episodes[-1], {
            'url': u'play/one-piece.ov8/1',
            'is_dir': False, 'image': '',
            'name': u"Episode 1 (Dec 25, 2016 - 10:39)"
        })
        self._sleep()

    def test_get_episode_sources(self):
        "get_episode_sources find onepiece's first episode"
        sources = self.browser.get_episode_sources('one-piece.ov8', 1)
        self.assertGreaterEqual(len(sources), 1)
        self._sleep()

if __name__ == "__main__":
    unittest.main()
