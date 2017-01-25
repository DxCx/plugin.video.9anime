#!/usr/bin/env python2

_REGISTERED_ROUTES = []

class route(object):
    def __init__(self,route_path):
        self._path = route_path
        self._is_wildcard = False
        if route_path.endswith("*"):
            self._is_wildcard = True
            self._path = route_path[:-1]

    def __call__(self, func):
        self._func = func
        self._register_route()
        def w(*args, **kargs):
            return w(*atgs, **kargs)
        return w

    def _register_route(self):
        _REGISTERED_ROUTES.append(self)

    @property
    def path(self):
        return self._path

    @property
    def wildcard(self):
        return self._is_wildcard

    @property
    def func(self):
        return self._func

def router_process(url):
    payload = "/".join(url.split("/")[1:])
    for route_obj in _REGISTERED_ROUTES:
        if (route_obj.wildcard and url.startswith(route_obj.path)) or (not route_obj.wildcard and url == route_obj.path):
            return route_obj.func(payload)
    return False
