#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
import unittest
import unittest.mock as mock

from gardenbot.weather import ForecastIODataSource

historical_filename = os.path.join(os.path.dirname(__file__), "response_data", "historical_response.json")
with open(historical_filename, "rt") as f:
    HISTORICAL_DATA = json.load(f)

class TestForecastIODataSource(unittest.TestCase):

    def setUp(self):
        self.data_source = ForecastIODataSource('')

    def tearDown(self):
        pass

    @mock.patch('gardenbot.weather.ForecastIODataSource._get_historical_data', return_value=HISTORICAL_DATA)
    def test_historical_rainfall(self, *mocks):
        pass
