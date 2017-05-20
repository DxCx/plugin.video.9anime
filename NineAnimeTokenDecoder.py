#!/usr/bin/python
# Author: @githubus11
#
# the + in the beginning parses text to a number
# a [] converts everything before into text -> therefore everythin before *10 or *100 or *1000
# '(+((!+[]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(+!![]+[])+(!+[]+!![]+[])))>>(!+[]+!![]+!![]+!![]+!![]+!![]+!![])'
# '(+((1+1+1+1+1+10)+(1+1+1+1+1+1+1+1+10)+(+10)+(1+10)))>>(1+1+1+1+1+1+1)'
# 0 is a marker for times 10 or more
# expands to
# '(+((1+1+1+1+1+1)*1000+(1+1+1+1+1+1+1+1+1)*100+(+1)*10+(1+1)*1))>>(1+1+1+1+1+1+1)'

import re
import math

class NineAnimeTokenDecoder:
    _function_name_regex = re.compile(ur'([^,]+)=function\(')
    _lines_regex_template = ur'{}\(([^\,a]+)\)'
    _outer_parentheses_group_regex = re.compile(ur'\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)')
    _TOKEN_COOKIE_NAME = 'reqkey'

    def __init__(self):
        pass

    @classmethod
    def decode_token(cls, token):
        lines = cls._get_lines_to_decode(token)
        chars = map(lambda x: cls._decode_as_char(x), lines)
        result = ''.join(chars)
        return result

    @classmethod
    def set_request(cls, tokenUrl, send_request):
        def _f(request):
            # TODO: Expires? when and how?
            if cls._TOKEN_COOKIE_NAME not in request.cookies:
                token = send_request(tokenUrl).text
                request.add_cookie(cls._TOKEN_COOKIE_NAME,
                                   cls.decode_token(token))
            return request
        return _f

    @classmethod
    def _get_lines_to_decode(cls, text):
        function_name = cls._find_function_name(text)
        lines_regex = cls._lines_regex_template.format(function_name)
        matches = list(re.findall(lines_regex, text))
        return matches

    @classmethod
    def _decode_as_int(cls, text):
        return cls._get_token_number(text)

    @classmethod
    def _decode_as_char(cls, text):
        num = cls._decode_as_int(text)
        return chr(num)

    @classmethod
    def _get_token_number(cls, text):
        # !![] should be +!![] but im using the extra + so all 1 get accumulated
        # will result in (1+1+1+1+1+1) instead of (111111)
        replaced = text.replace('!+[]', '1').replace('!![]', '1').replace('+[]', '0')
        expanded = cls._recursive_token_multiplier(replaced)
        return eval(expanded)

    @classmethod
    def _recursive_token_multiplier(cls, text):
        matches = cls._outer_parentheses_group_regex.findall(text)
        result = text
        for valNum, val in enumerate(matches):
            if not val.endswith('0)'):
                result = result.replace(val, '(' +
                                        cls._recursive_token_multiplier(cls._remove_parenthesis(val)) + ')', 1)
            else:
                multiplier = int(math.pow(10, len(matches) - 1 - valNum))
                result = result.replace(val, val.replace('0)', ')*{}'.format(multiplier)), 1)

        return result

    @classmethod
    def _remove_parenthesis(cls, text):
        if text.startswith('(') and text.endswith(')'):
            return (text[1:])[:-1]
        return text

    @classmethod
    def _find_function_name(cls, text):
        res = cls._function_name_regex.search(text, re.UNICODE)
        return res.groups()[0]
