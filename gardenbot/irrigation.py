#!/usr/bin/env python
# -*- coding: utf-8 -*-


GALLONS_PER_SQFT_INCH = 0.6


class IrrigationInfo(object):

    def __init__(self, sqft, gpm):
        self._sqft = sqft
        self._gpm = gpm

    @property
    def sqft(self):
        return self._sqft

    def minutes_to_irrigate(self, water_inches):
        return (self._sqft * water_inches) * GALLONS_PER_SQFT_INCH / self._gpm
