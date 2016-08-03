#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
import unittest

from datetime import date, timedelta
from unittest.mock import Mock, patch
from gardenbot.weather import ForecastIODataSource

historical_filename = os.path.join(os.path.dirname(__file__), "response_data", "historical_response.json")
with open(historical_filename, "rt") as f:
    HISTORICAL_RESPONSE = Mock(status_code=200, json=Mock(return_value=json.load(f)))


class TestForecastIODataSource(unittest.TestCase):

    def setUp(self):
        self.data_source = ForecastIODataSource('')

    def tearDown(self):
        pass

    @patch('gardenbot.weather.ForecastIODataSource._get_historical_data', return_value=HISTORICAL_RESPONSE)
    def test_historical_rainfall(self, *mocks):
        yesterday = date.today() - timedelta(days=1)
        location = Mock(latitude=44.0, longitude=44.0)
        import pdb; pdb.set_trace()
        actual = self.data_source.get_rainfall(location, yesterday)
        self.assertIsNotNone(actual)
