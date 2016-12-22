# -*- coding: UTF-8 -*-
import hashlib
import time

import requests


class TaoPiaoPao:
    def __init__(self):
        self.requests = requests.session()
        self.requests.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
            'Connection': 'keep-alive',
            'Referer': 'https://h5.m.taobao.com'
        }
        self.url = 'https://api.m.taobao.com/h5/{}/4.0/'

    def _get_json_from_html(self, api, data):
        params = {}
        params['v'] = '4.0'
        params['api'] = api
        params['appKey'] = '12574478'
        params['t'] = str(int(time.time() * 1000))
        params['callback'] = 'mtopjsonp2'
        params['type'] = 'json'
        params['data'] = str(dict(platform='8', asac='D679AU6J95PHQT67G0B5', **data))
        params['sign'] = self._make_sign(self.url.format(api), params)
        res = self.requests.get(url=self.url.format(api), params=params)
        return res.json()

    def _make_sign(self, url, params):
        _m_h5_tk = self.requests.cookies.get('_m_h5_tk') or self.requests.get(url, params=params).cookies.get(
            '_m_h5_tk')
        s = '&'.join([_m_h5_tk.split('_')[0], params['t'], '12574478', str(params['data'])])
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        return m.hexdigest()

    def get_city(self):
        citys = self._get_json_from_html(
            'http://dianying.taobao.com/cityAction.json?action=cityAction&event_submit_doGetAllRegion=true')[
            'returnValue']
        return citys

    def get_cinemas(self, city_id):
        data = {"longitude": 0, "latitude": 0, "supportTypeCode": "1",
                "cityCode": city_id, "cinemasInclude": "14",
                "field": "i:id;cinemaName;address;regionName;distance;scheduleCloseTime;activities;availableScheduleCount;availableTodayScheduleCount;supportDate;showMark;cinemaSeatPrice;specialFlag;availableCouponCount;shows;supportFLag;specialRemind;specialSchedules;longitude;latitude",
                "pageCode": "APP_CINEMA"}
        cinemas = self._get_json_from_html('mtop.film.MtopCinemaAPI.getMixupCinemas', data)
        return cinemas

    def get_movie(self, city_id):
        data = {'citycode': city_id}
        movies = self._get_json_from_html('mtop.film.mtopshowapi.getshowsbycitycode', data)
        return movies

    def get_cinema_movie_sched(self, cinema_id, movieid=''):
        date = {'days': 50, "cinemaid": cinema_id, 'showid': movieid}
        sched = self._get_json_from_html('mtop.film.mtopshowapi.getshowsbycinemaid', date)
        return sched


if __name__ == '__main__':
    my = TaoPiaoPao()
    # print(my.get_city())
    # print(my.get_cinemas(310100))
    # print(my.get_movie(420100))
    # print(my.get_cinema_movie_sched(22289, '4420'))
