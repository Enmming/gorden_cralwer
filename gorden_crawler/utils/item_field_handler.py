# -*- coding: utf-8 -*-
import re


def handle_price(price_str):
    if price_str:
        #处理字符串，把单位去除
        tmp_str = re.sub(r'^[^0-9\.]+', '', price_str, 1)
        return re.sub(r'[^0-9\.]', '', tmp_str)
    else:
        return ''


def handle_no_http(http_str):
    if not re.match(r'^http[s]?:.+', http_str):
        http_str = 'http:' + http_str
        
    return http_str
