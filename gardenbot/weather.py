#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
from functools import lru_cache
from datetime import date, datetime


class WeatherInfo(object):
    """Represents the weather information for a given location and time.

    Has attributes for relevant weather metrics over the configured interval.
    """
    def accumulated_rainfall_3_day(self):
        pass

    def expected_rainfall_4_day(self):
        pass

    def average_daily_temperature(self):
        pass


class DataSource(object):
    def get_rainfall(self, location, d, **kwargs):
        """Returns the rainfall for the location on the date specified.
        """
        raise NotImplementedError

    def get_temperature_range(self, location, d, **kwargs):
        """Returns the temperature range for the locaiton on the date specified.
        """
        raise NotImplementedError


class ForecastIODataSource(object):
    base_url = "https://api.forecast.io"
    forecast_url_template = base_url + "forecast/{apikey}/{latitude},{longitude}"
    time_machine_url_template = forecast_url_template + ",{time}"
    time_format_str = "%Y-%m-%d%H:%M:%S"
    cache_size = 512

    def __init__(self, api_key):
        self._api_key = api_key

    def _url_with_qargs(self, url_template, location, d=None, query_params={}):
        time = d.strftime(self.time_format_str)
        url = url_template.format(apikey=self._api_key, latitude=location.latitude, longitude=location.longitude, time=time)
        if query_params:
            url += "?" + "&".join("{}={}".format(key, value) for key, value in query_params.items())
        return url

    @lru_cache(maxsize=cache_size)
    def _get_historical_data(self, location, d):
        # TODO: set excludes for more efficient requests
        query_params = dict(exclude="[]")
        url = self._url_with_qargs(self.time_machine_url_template, location, d, query_params)
        return requests.get(url)

    @lru_cache(maxsize=cache_size)
    def _get_forecast_data(self, location):
        # TODO: set excludes for more efficient requests
        query_params = dict(exclude="[]")
        url = self._url_with_qargs(self.forecast_url_template, location, query_params=query_params)
        return requests.get(url)

    def _get_historical_rainfall(self, location, d):
        response = self._get_historical_data(location, d)
        if response.status_code != 200:
            return None

        hourly_data = response.json()['hourly']['data']
        accumulated_rainfall = sum(hr['precipIntensity'] for hr in hourly_data if hr.get('precipType') == 'rain')
        return accumulated_rainfall

    def _get_forecasted_rainfall(self, location):
        response = self._get_forecast_data(location)
        if response.status_code != 200:
            return None

        hourly_data = response.json()['hourly']['data']
        # can we make a more accurate prediction than the best case?
        # we need to look more than two days in the future
        accumulated_rainfall = sum(hr['precipIntensity'] for hr in hourly_data if hr.get('precipType') == 'rain')
        return accumulated_rainfall

    def get_rainfall(self, location, d):
        if d <= date.today():
            return self._get_historical_rainfall(location, d)
        else:
            return self._get_forecasted_rainfall(location)
