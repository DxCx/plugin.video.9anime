import re
from string import ascii_lowercase as lc, ascii_uppercase as uc, maketrans

class NineAnimeUrlExtender:
    _TS_MAP_TABLE = [i for i in uc if ord(i) % 2 != 0] + [i for i in uc if ord(i) % 2 == 0]
    _ts_value_regex = re.compile(ur"<body.*data-ts\s*=[\"]([^\"]+?)[\"]")
    _server_value_regex = \
    re.compile(ur"<div\sclass=\"server\srow\"\s.+?data-id=\"(\d+)\".*?>(.+?)\<\/div\>")
    _active_ep_regex = re.compile(ur"\<a\sclass=\"active\".+?")

    def __init__(self):
        pass

    @classmethod
    def rot_dict(cls, obj):
        newObj = {}

        for key, value in obj.iteritems():
            if type(value) is unicode or type(value) is str:
                if value.startswith('.'):
                    newObj[key] = cls.rot_string(value[1:])
                else:
                    newObj[key] = value
            elif type(value) is dict:
                newObj[key] = cls.rot_dict(value)
            else:
                newObj[key] = value

        return newObj

    @classmethod
    def rot_string(cls, content):
        RotBy = 8
        lookup = maketrans(lc + uc, lc[RotBy:] + lc[:RotBy] + uc[RotBy:] + uc[:RotBy])
        decoded = str(content).translate(lookup)
        return decoded

    @classmethod
    def get_server_value(cls, content):
        server_values = cls._server_value_regex.findall(content)
        for (server_id, episodes) in server_values:
            if len(cls._active_ep_regex.findall(episodes)):
                return int(server_id, 10)

        raise Exception("Cant extract server id")

    @classmethod
    def get_ts_value(cls, content):
        ts_value = cls._ts_value_regex.findall(content)[0]
        return cls._decode_ts_value(ts_value)

    @classmethod
    def _decode_ts_value(cls, ts):
        decoded = ""
        for c in ts:
            replaced = False
            if c not in cls._TS_MAP_TABLE:
                decoded += c
                continue
            decoded += uc[cls._TS_MAP_TABLE.index(c)]

        return decoded.decode("base64")

    @classmethod
    def get_extra_url_parameter(cls, id, update, server, ts):
        DD = 'gIXCaNh'
        params = [
            ('id', str(id)),
            ('update', str(update)),
            ('ts', str(ts)),
            ('server', str(server)),
        ]

        o = cls._s(DD)
        for i in params:
            o += cls._s(cls._a(DD + i[0], i[1]))

        return o

    @classmethod
    def _s(cls, t):
        i = 0
        for (e, c) in enumerate(t):
            i += ord(c) * e
        return i

    @classmethod
    def _a(cls, t, e):
        n = 0
        for i in range(max(len(t), len(e))):
            n += ord(e[i]) if i < len(e) else 0
            n += ord(t[i]) if i < len(t) else 0
        return format(n, 'x')  # convert n to hex string
