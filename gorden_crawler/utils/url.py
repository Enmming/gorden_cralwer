# -*- coding: utf-8 -*-
import urlparse, copy, urllib

def url_values_plus(url, key, val):
    u = urlparse.urlparse(url)
    qs = u.query
    pure_url = url.replace('?'+qs, '')
    qs_dict = dict(urlparse.parse_qsl(qs))
    tmp_dict = copy.deepcopy(qs_dict)
    tmp_dict[key] = val
    tmp_qs = urllib.unquote(urllib.urlencode(tmp_dict))
    return pure_url + "?" + tmp_qs
