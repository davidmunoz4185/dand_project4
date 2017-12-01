#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re


tipo_via_set = [
    'Avenida',
    'Calle',
    'Camino',
    'Paseo',
    'Plaza',
    'Carrera',
    'Ronda',
    'Carretera',
    'Pasaje'
]


POSTCODE_PATTERN = re.compile(r'^(E)?(28[0-9]{3})')


def split_by_char(string_in, char_in, pos_in, pos_out, set_in):
    first_field = string_in.split(char_in)[pos_in-1]
    if first_field in set_in and char_in in string_in:
        return string_in.split(char_in)[pos_out-1]
    return string_in


def treat_tipo_via(string_in):
    string_out = string_in
    if string_out not in tipo_via_set:
        string_out = split_by_char(string_out, " ", 1, 1, tipo_via_set)
        string_out = string_out.upper()[:1] + string_out.lower()[1:]
        if string_out not in tipo_via_set:
            return "wrong value [{}]".format(string_in)
    return string_out


def treat_postcode(string_in):
    string_out = "28000"
    m = POSTCODE_PATTERN.search(string_in)
    if m:
        return m.group(2)
    return string_out
