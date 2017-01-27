#!/usr/local/bin/python2
import unittest
import time
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
        self.assertGreaterEqual(len(search_res), 1)
        self.assertEqual(search_res[0], {
            'url': 'animes/naruto-shippuuden-dub.00zr/',
            'is_dir': True,
            'image': search_res[0]['image'],
            'name': 'Naruto: Shippuuden (Dub)'
        })
        self._sleep()

    def test_search_with_pages(self):
        "search 'Dragon' and verify pages"
        search_res = self.browser.search_site("Dragon")
        self.assertEqual(len(search_res), 33)
        self.assertEqual(search_res[-1], {
            'name': 'Next Page (2/4)',
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
        self.assertEqual(latest[-1], {
            'name': 'Next Page (2/190)',
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
        self.assertEqual(newest[-1], {
            'name': 'Next Page (2/190)',
            'is_dir': True,
            'image': None,
            'url': 'newest/2'
        })
        self._sleep()

    def test_get_genres(self):
        "get_genres returns genere list"
        genre_list = self.browser.get_genres()
        self.assertGreater(len(genre_list), 10)
        self.assertEqual(genre_list[0], {
            'url': 'genre/action/1',
            'is_dir': True,
            'image': '',
            'name': 'Action'
        })
        self._sleep()

    def test_get_genre(self):
        "get_genres returns anime list by genre"
        anime_list = self.browser.get_genre("action")
        self.assertGreater(len(anime_list), 10)
        self.assertEqual(anime_list[0], {
            'url': 'animes/tales-of-zestiria-the-x-2nd-season-dub.m8nv/',
            'is_dir': True,
            'image': anime_list[0]['image'],
            'name': 'Tales of Zestiria the X 2nd Season (Dub)'
        })
        self._sleep()

    #def test_get_anime_episodes(self):
    #    "get_anime_episodes works for one-piece"
    #    episodes = self.browser.get_anime_episodes("one-piece")
    #    self.assertEqual(len(episodes) > 750, True)
    #    self.assertEqual(episodes[-1], {
    #        'url': 'play/one-piece/1',
    #        'is_dir': False, 'image': '',
    #        'name': "One Piece 1 : I'm Luffy! The boy who will become the Pirate King!"
    #    })

    #def test_search_site_pages(self):
    #    "search site finds with page"
    #    search_res = self.browser.search_site("Naruto Shippuden", 1)
    #    self.assertGreaterEqual(len(search_res), 1)
    #    self.assertEqual(search_res[0], {
    #        'url': 'animes/naruto-shippuuden-dub.00zr/',
    #        'is_dir': True,
    #        'image': search_res[0]['image'],
    #        'name': 'Naruto: Shippuuden (Dub)'
    #    })

    #def test_get_episode_sources(self):
    #    "get_episode_sources find nartuo's first episode"
    #    sources = self.browser.get_episode_sources('naruto-shippuden/1')
    #    self.assertGreater(len(sources), 10)

if __name__ == "__main__":
    unittest.main()
