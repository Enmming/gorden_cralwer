import base64
import re
import datetime
import random
import os


class AsiaOpenProxyRandomMiddleware(object):
    def process_request(self, request, spider):
        proxy_ips = [
            'https://sg.proxymesh.com:31280',
            'https://jp.proxymesh.com:31280',
        ]
        randint = random.randint(0, len(proxy_ips) - 1)
        randip = proxy_ips[randint]
        request.meta['proxy'] = randip


class OpenProxyRandomMiddleware(object):
    def process_request(self, request, spider):
        proxy_ips = [
            'https://us-dc.proxymesh.com:31280',
            #             'https://us-fl.proxymesh.com:31280',
            #             'https://de.proxymesh.com:31280',
            #             'https://nl.proxymesh.com:31280',
            # 'https://sg.proxymesh.com:31280',
            # 'https://jp.proxymesh.com:31280',
            #             'https://ch.proxymesh.com:31280',
            'https://us-ca.proxymesh.com:31280',
            'https://us-ny.proxymesh.com:31280',
            'https://us-il.proxymesh.com:31280',
            #             'https://uk.proxymesh.com:31280',
        ]

        #         if os.environ['yelp_country'] == 'hk' or os.environ['yelp_country'] == 'tw' or os.environ['yelp_country'] == 'sg':
        #             proxy_ips = [
        #                 'https://sg.proxymesh.com:31280',
        #                 'https://jp.proxymesh.com:31280',
        #             ]
        #         elif os.environ['yelp_country'] == 'uk' or os.environ['yelp_country'] == 'de' or os.environ['yelp_country'] == 'nl':
        #             proxy_ips = [
        #                 'https://uk.proxymesh.com:31280',
        #             ]
        #         elif os.environ['yelp_country'] == 'usa':
        #             proxy_ips = [
        # #             'https://us-dc.proxymesh.com:31280',
        # #             'https://us-fl.proxymesh.com:31280',
        #             'https://us-ca.proxymesh.com:31280',
        # #             'https://us-ny.proxymesh.com:31280',
        # #             'https://us-il.proxymesh.com:31280',
        #         ]


        randint = random.randint(0, len(proxy_ips) - 1)
        randip = proxy_ips[randint]
        request.meta['proxy'] = randip

    #         print 'ip: ' + randip
    # "https://us-il.proxymesh.com:31280"

    # request.meta['proxy'] = "http://45.63.58.8:8080"
    # proxy_user_pass = "root:wniiroacp!7"


# proxy_user_pass = "reeves:11111111"
#         encoded_user_pass = base64.encodestring(proxy_user_pass)
#         request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass

class OpenProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us-ny.proxymesh.com:31280"  # "http://45.63.58.8:8080"

        # request.meta['proxy'] = "http://45.63.58.8:8080"
        # proxy_user_pass = "root:wniiroacp!7"
        proxy_user_pass = "reeves:11111111"
        encoded_user_pass = base64.encodestring(proxy_user_pass)
        request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        url = request.url

        today = datetime.date.today()
        today_day = int(today.strftime("%d"))

        #         if not re.match(r"^https", url):

        today_proxy = today_day % 3

        if today_proxy == 0:
            request.meta['proxy'] = "https://us.proxymesh.com:31280"  # "http://45.63.58.8:8080"
        elif today_proxy == 1:
            request.meta['proxy'] = "https://us-dc.proxymesh.com:31280"  # "http://45.63.58.8:8080"
        else:
            request.meta['proxy'] = "https://us-il.proxymesh.com:31280"  # "http://45.63.58.8:8080"
        #         request.meta['proxy'] = "http://45.63.58.8:8080"
        # proxy_user_pass = "root:wniiroacp!7"
        proxy_user_pass = "reeves:11111111"
        encoded_user_pass = base64.encodestring(proxy_user_pass)
        request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass

# else:
#             request.headers['Proxy-Authorization'] = ''
#             request.meta['proxy'] = ''


class ProxyWeeklyRandomHttpsMiddleware(object):
    def process_request(self, request, spider):
        today = datetime.date.today()
        today_day = int(today.strftime("%d"))

        today_proxy = today_day % 3

        if today_proxy == 0:
            request.meta['proxy'] = "https://us-wa.proxymesh.com:31280"  # "http://45.63.58.8:8080"
        elif today_proxy == 1:
            request.meta['proxy'] = "https://us-dc.proxymesh.com:31280"  # "http://45.63.58.8:8080"
        else:
            request.meta['proxy'] = "https://us-ca.proxymesh.com:31280"  # "http://45.63.58.8:8080"


class ProxyHttpsMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us-il.proxymesh.com:31280"


class ProxyUSAMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us.proxymesh.com:31280"
        proxy_user_pass = "reeves:11111111"
        encoded_user_pass = base64.encodestring(proxy_user_pass)
        request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass


class ProxyGiltMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = 'https://au.proxymesh.com:31280'


class ProxyUKMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://uk.proxymesh.com:31280"


class ProxyHttpsUSAMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us.proxymesh.com:31280"


class ProxynHttpsNLMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://nl.proxymesh.com:31280"

class ProxynHttpsSGMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://sg.proxymesh.com:31280"



class ProxyHttpsRandomMiddleware(object):
    def process_request(self, request, spider):
        us_proxies = [
            "https://us-il.proxymesh.com:31280",
            "https://us-ca.proxymesh.com:31280",
            "https://us-dc.proxymesh.com:31280",
            "https://us-fl.proxymesh.com:31280",
            "https://us-wa.proxymesh.com:31280",
            "https://us-ny.proxymesh.com:31280",
            "https://us.proxymesh.com:31280",
            "https://uk.proxymesh.com:31280",
            'https://au.proxymesh.com:31280',
            "https://nl.proxymesh.com:31280",
            "https://sg.proxymesh.com:31280",
            ""
        ]
        proxy = random.choice(us_proxies)
        request.meta['proxy'] = proxy


class ProxyHttpsUSAILMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us-il.proxymesh.com:31280"


class ProxyHttpsUSACAMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us-ca.proxymesh.com:31280"


class ProxyHttpsUSADCMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us-dc.proxymesh.com:31280"


class ProxyHttpsUSAFLMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us-fl.proxymesh.com:31280"


class ProxyHttpsUSAWAMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "https://us-wa.proxymesh.com:31280"
