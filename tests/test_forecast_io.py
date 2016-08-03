#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
import unittest

from datetime import date, timedelta
from unittest.mock import Mock, patch
from gardenbot.weather import ForecastIODataSource


# historical fixture
historical_filename = os.path.join(os.path.dirname(__file__), "response_data", "historical_response.json")
with open(historical_filename, "rt") as f:
    HISTORICAL_RESPONSE = Mock(status_code=200, json=Mock(return_value=json.load(f)))

# forecast fixture
forecast_filename = os.path.join(os.path.dirname(__file__), "response_data", "forecast_response.json")
with open(forecast_filename, "rt") as f:
    FORECAST_RESPONSE = Mock(status_code=200, json=Mock(return_value=json.load(f)))


class TestForecastIODataSource(unittest.TestCase):

    def setUp(self):
        self.data_source = ForecastIODataSource('')

    def tearDown(self):
        pass

    @patch('gardenbot.weather.ForecastIODataSource._get_historical_data', return_value=HISTORICAL_RESPONSE)
    def test_historical_rainfall(self, get_data_mock):
        yesterday = date.today() - timedelta(days=1)
        location = Mock(latitude=44.0, longitude=44.0)
        actual = self.data_source.get_rainfall(location, yesterday)
        self.assertIsNotNone(actual)
        self.assertEqual(1, len(get_data_mock.mock_calls))

    @patch('gardenbot.weather.ForecastIODataSource._get_historical_data', return_value=HISTORICAL_RESPONSE)
    def test_historical_rainfall_equal(self, get_data_mock):
        location = Mock(latitude=44.0, longitude=44.0)
        self.data_source.get_rainfall(location, date.today())
        self.assertEqual(1, len(get_data_mock.mock_calls))

    @patch('gardenbot.weather.ForecastIODataSource._get_forecast_data', return_value=FORECAST_RESPONSE)
    def test_forecasted_rainfall(self, get_data_mock):
        tomorrow = date.today() + timedelta(days=1)
        location = Mock(latitude=44.0, longitude=44.0)
        actual = self.data_source.get_rainfall(location, tomorrow)
        self.assertIsNotNone(actual)
        self.assertEqual(1, len(get_data_mock.mock_calls))
