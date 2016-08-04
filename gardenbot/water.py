#!/usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import date, timedelta

BASE_TEMP = 60
BASE_INCHES = 1.0
INCH_INCREMENT = 0.5
TEMP_INCREMENT = 10

class WaterInfo(object):

    def __init__(self, location, weather_info):
        self._weather_info = weather_info
        self._location = location

    @property
    def start_date(self):
        """First date of the range for this data."""
        return date.today() - timedelta(days=3)

    @property
    def end_date(self):
        """Last date of the range for this data"""
        return date.today() + timedelta(days=3)

    @property
    def accumulated_rainfall(self):
        """Accumulated rainfall so far this 7 day period."""
        return self._weather_info.accumulated_rainfall_3_day(self._location)

    @property
    def expected_rainfall(self):
        """Predicted amount of rainfall."""
        return self._weather_info.expected_rainfall_4_day(self._location)

    @property
    def total_rainfall(self):
        """Sum of accumulated and expected rainfall."""
        return self.accumulated_rainfall + self.expected_rainfall

    @property
    def average_temperature(self):
        """Average temperature in the date range"""
        return self._weather_info.average_rolling_7_temperature(self._location)

    @property
    def location(self):
        """Location of watering requirements."""
        return self._location

    @property
    def temperature_triggered_water_adjustment(self):
        return (self.average_temperature - BASE_TEMP) / TEMP_INCREMENT * INCH_INCREMENT

    @property
    def minimum_watering_requirements(self):
        """Minimum amount of water needed."""
        return BASE_INCHES + self.temperature_triggered_water_adjustment

    @property
    def required_external_water_inches(self):
        """Amount of water you need to add, in inches."""
        return self.minimum_watering_requirements - self.accumulated_rainfall - self.expected_rainfall
