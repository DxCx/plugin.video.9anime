import re
from string import ascii_lowercase as lc, ascii_uppercase as uc, maketrans

class NineAnimeUrlExtender:
    # _TS_MAP_TABLE = [i for i in uc if ord(i) % 2 != 0] + [i for i in uc if ord(i) % 2 == 0]
    _CUSB64_MAP_TABLE = [i for i in lc if ord(i) % 2 != 0] + [i for i in lc if ord(i) % 2 == 0]
    _ts_value_regex = re.compile(ur"<html.*data-ts\s*=[\"]([^\"]+?)[\"]")
    _server_value_regex = \
    re.compile(ur"\<div\sclass=\"widget-title\"\>\s(.+?)\s\<\/div\>")
    _active_server_regex = \
    re.compile(ur"\<span\sclass=\"tab active\"\sdata-name=\"(\d+)\".+?")

    def __init__(self):
        pass

    @classmethod
    def decode_info(cls, obj):
        newObj = {}

        for key, value in obj.iteritems():
            if type(value) is unicode or type(value) is str:
                if value.startswith('.'):
                    newObj[key] = cls._rot_string(value[1:])
                if value.startswith('-'):
                    newObj[key] = cls._cusb64_string(value[1:])
                else:
                    newObj[key] = value
            elif type(value) is dict:
                newObj[key] = cls.decode_info(value)
            else:
                newObj[key] = value

        return newObj

    @classmethod
    def get_server_value(cls, content):
        servers = cls._server_value_regex.findall(content)[0]
        active_server = cls._active_server_regex.findall(servers)
        if len(active_server) != 1:
            raise Exception("Cant extract server id")
        return int(active_server[0], 10)

    @classmethod
    def get_ts_value(cls, content):
        ts_value = cls._ts_value_regex.findall(content)[0]
        return ts_value
        # return cls._decode_ts_value(ts_value)

    @classmethod
    def _rot_string(cls, content):
        RotBy = 8
        lookup = maketrans(lc + uc, lc[RotBy:] + lc[:RotBy] + uc[RotBy:] + uc[:RotBy])
        decoded = str(content).translate(lookup)
        return decoded

    # @classmethod
    # def _decode_ts_value(cls, ts):
    #     decoded = ""
    #     for c in ts:
    #         replaced = False
    #         if c not in cls._TS_MAP_TABLE:
    #             decoded += c
    #             continue
    #         decoded += uc[cls._TS_MAP_TABLE.index(c)]

    #     missing_padding = len(decoded) % 4
    #     if missing_padding:
    #         decoded += b'=' * (4 - missing_padding)
    #     return decoded.decode("base64")

    @classmethod
    def _cusb64_string(cls, content):
        decoded = ""
        for c in content:
            replaced = False
            if c not in cls._CUSB64_MAP_TABLE:
                decoded += c
                continue
            decoded += lc[cls._CUSB64_MAP_TABLE.index(c)]

        missing_padding = len(decoded) % 4
        if missing_padding:
            decoded += b'=' * (4 - missing_padding)
        return decoded.decode("base64")

    @classmethod
    def get_extra_url_parameter(cls, id, server, ts):
        DD = 'bVZX0bdD'
        params = [
            ('id', str(id)),
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
            i += ord(c) + e
        return i

    @classmethod
    def _a(cls, t, e):
        n = 0
        for i in range(max(len(t), len(e))):
            n += ord(e[i]) if i < len(e) else 0
            n += ord(t[i]) if i < len(t) else 0
        return format(n, 'x')  # convert n to hex string
