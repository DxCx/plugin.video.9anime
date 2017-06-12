import re


class NineAnimeUrlExtender:
    _ts_value_regex = re.compile(ur"<body.*data-ts\s*=['\"](\d+)['\"]")

    def __init__(self):
        pass

    @classmethod
    def get_ts_value(cls, content):
        return cls._ts_value_regex.findall(content)[0]

    @classmethod
    def get_extra_url_parameter(cls, id, update, ts):
        DD = 'gIXCaNh'
        params = [('id', str(id)), ('update', str(update)), ('ts', str(ts))]

        o = cls._s(DD)
        for i in params:
            o += cls._s(cls._a(DD + i[0], i[1]))

        return o

    @classmethod
    def _s(cls, t):
        i = 0
        for (e, c) in enumerate(t):
            i += ord(c) * e + e
        return i

    @classmethod
    def _a(cls, t, e):
        n = 0
        for i in range(max(len(t), len(e))):
            n += ord(e[i]) if i < len(e) else 0
            n += ord(t[i]) if i < len(t) else 0
        return format(n, 'x')  # convert n to hex string
