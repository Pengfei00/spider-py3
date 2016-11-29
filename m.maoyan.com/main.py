# -*- coding: UTF-8 -*-
import re

import requests


class MaoYan:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
            'Connection': 'keep-alive',
            'Referer': 'http://m.maoyan.com'
        }

    def _get_json_from_html(self, url, cookies=None, headers=None):
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = {}
        assert isinstance(cookies, dict)
        assert isinstance(headers, dict)
        res = requests.get(url=url, headers=dict(self.headers, **headers), cookies=cookies)
        return res.json()

    def get_city(self):
        citys = self._get_json_from_html('http://m.maoyan.com/changecity.json')['data']['CityMap']
        return citys

    def get_cinemas(self, city_id):
        cinemas = self._get_json_from_html('http://m.maoyan.com/cinemas.json', cookies=dict(ci=str(city_id)))['data']
        return cinemas

    def get_movie(self, hot=True, limit=1000):
        movies = self._get_json_from_html(
            'http://m.maoyan.com/movie/list.json?type={}&offset=0&limit={}'.format('hot' if hot else 'coming', limit))[
            'data']['movies']
        return movies

    def get_cinema_movie_sched(self, cinema, movie=''):
        url = 'http://m.maoyan.com/showtime/wrap.json?cinemaid={}&movieid={}'.format(cinema, movie)
        sched = self._get_json_from_html(url)['data']
        css = sched.get('cssLink')
        sched = sched.get('DateShow')
        css = requests.get(css).text.split('\n')[2:-1]
        csspr = {}
        for i in css:
            pos = re.search('true(\d+)>.*?\((\d+)\).*?:-(.*?)em;width:(.*?)em;}', i).groups()
            csspr['{}'.format(pos[0])] = {'{}'.format(pos[1]): [int(float(pos[2]) / 0.55), int(float(pos[3]) / 0.55)]}
        for date in sched:
            for i in sched[date]:
                prStr = re.search('<span class="m3 true(\d+)">(.*?)</span>', i['prStr']).groups()
                sellPrStr = re.search('<span class="m3 true(\d+)">(.*?)</span>', i['sellPrStr']).groups()
                tmppr = []
                tmpsell = []
                for index, line in enumerate(filter(lambda x: x != '', prStr[1].replace('<i>', '').split('</i>'))):
                    sl = csspr[prStr[0]][str(index + 1)]
                    tmppr.append(line[sl[0]:sl[0] + sl[1]])
                for index, line in enumerate(filter(lambda x: x != '', sellPrStr[1].replace('<i>', '').split('</i>'))):
                    sl = csspr[sellPrStr[0]][str(index + 1)]
                    tmpsell.append(line[sl[0]:sl[0] + sl[1]])
                i['prStr'] = ''.join(tmppr)
                i['sellPrStr'] = ''.join(tmpsell)
        return sched


if __name__ == '__main__':
    my = MaoYan()
    print(my.get_city())
    print(my.get_cinemas(1))
    print(my.get_movie(hot=False))
    print(my.get_cinema_movie_sched(48))
