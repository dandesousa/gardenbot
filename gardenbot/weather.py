#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import statistics
from time import mktime
from functools import lru_cache
from datetime import date, timedelta


class WeatherInfo(object):
    """Represents the weather information for a given location and time.

    Has attributes for relevant weather metrics over the configured interval.
    """
    def __init__(self, data_source):
        self._data_source = data_source

    def accumulated_rainfall_3_day(self, location):
        accumulated_rainfall = 0
        for i in range(1, 4):
            day = date.today() - timedelta(days=i)
            rainfall = self._data_source.get_rainfall(location, day)
            if rainfall is not None:
                accumulated_rainfall += rainfall
        return accumulated_rainfall

    def expected_rainfall_4_day(self, location):
        # gets all forecasted rainfall for today and going forward
        expected_rainfall = self._data_source.get_rainfall(location, date.today())
        return expected_rainfall

    def average_rolling_7_temperature(self, location):
        # I know this isn't right, but maybe best we can do given API limits
        window = (date.today() + timedelta(days=i) for i in range(-3, 4))
        temps = [self._data_source.get_avg_temperature(location, day) for day in window]
        return statistics.mean([temp for temp in temps if temp is not None])


class DataSource(object):
    def get_rainfall(self, location, d, **kwargs):
        """Returns the rainfall for the location on the date specified.
        """
        raise NotImplementedError

    def get_avg_temperature(self, location, d, **kwargs):
        """Returns the temperature range for the locaiton on the date specified.
        """
        raise NotImplementedError


class ForecastIODataSource(object):
    base_url = "https://api.forecast.io/"
    forecast_url_template = base_url + "forecast/{apikey}/{latitude},{longitude}"
    time_machine_url_template = forecast_url_template + ",{time}"
    time_format_str = "%Y-%m-%dT%H:%M:%S"
    cache_size = 512

    def __init__(self, api_key):
        self._api_key = api_key

    def _url_with_qargs(self, url_template, lat, lon, d=None, query_params={}):
        if d:
            time = d.strftime(self.time_format_str)
            url = url_template.format(apikey=self._api_key, latitude=lat, longitude=lon, time=time)
        else:
            url = url_template.format(apikey=self._api_key, latitude=lat, longitude=lon)

        if query_params:
            url += "?" + "&".join("{}={}".format(key, value) for key, value in query_params.items())
        return url

    @lru_cache(maxsize=cache_size)
    def _get_historical_data(self, lat, lon, d):
        # TODO: set excludes for more efficient requests
        query_params = dict(exclude="[]")
        url = self._url_with_qargs(self.time_machine_url_template, lat, lon, d, query_params)
        return requests.get(url)

    @lru_cache(maxsize=cache_size)
    def _get_forecast_data(self, lat, lon):
        # TODO: set excludes for more efficient requests
        query_params = dict(exclude="[]")
        url = self._url_with_qargs(self.forecast_url_template, lat, lon, query_params=query_params)
        return requests.get(url)

    def _get_historical_rainfall(self, location, d):
        response = self._get_historical_data(location.latitude, location.longitude, d)
        if response.status_code != 200:
            return None

        hourly_data = response.json()['hourly']['data']
        accumulated_rainfall = sum(hr.get('precipIntensity', 0) for hr in hourly_data if hr.get('precipType') == 'rain')
        return accumulated_rainfall

    def _get_forecasted_rainfall(self, location):
        response = self._get_forecast_data(location.latitude, location.longitude)
        if response.status_code != 200:
            return None

        hourly_data = response.json()['hourly']['data']
        # can we make a more accurate prediction than the best case?
        # we need to look more than two days in the future
        accumulated_rainfall = sum(hr.get('precipIntensity', 0) for hr in hourly_data if hr.get('precipType') == 'rain')
        return accumulated_rainfall

    def _get_historical_avg_temperature(self, location, d):
        response = self._get_historical_data(location.latitude, location.longitude, d)
        if response.status_code != 200:
            return None
        hourly_data = response.json()['hourly']['data']
        return statistics.mean(hr['temperature'] for hr in hourly_data)

    def _get_forecasted_avg_temperature(self, location, d):
        response = self._get_forecast_data(location.latitude, location.longitude)
        if response.status_code != 200:
            return None
        time = int(mktime(d.timetuple()))
        daily_data = response.json()['daily']['data']
        for day in daily_data:
            if day['time'] == time:
                return statistics.mean([day['temperatureMin'], day['temperatureMax']])
        return None

    def get_rainfall(self, location, d):
        if d <= date.today():
            return self._get_historical_rainfall(location, d)
        else:
            return self._get_forecasted_rainfall(location)

    # TODO: known bug here -- with time zones and incorrectly finding forcasted date.
    def get_avg_temperature(self, location, d, **kwargs):
        if d <= date.today():
            return self._get_historical_avg_temperature(location, d)
        else:
            return self._get_forecasted_avg_temperature(location, d)
