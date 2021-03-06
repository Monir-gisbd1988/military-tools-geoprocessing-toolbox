# coding: utf-8
'''
-----------------------------------------------------------------------------
Copyright 2016 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------------------

==================================================
RangeRingTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the range ring tests.

==================================================
history:
3/30/2016 - mf - original coding
5/23/2016 - mf - update for framework
==================================================
'''

import unittest
import logging
import Configuration

from . import RangeRingUtilsTestCase

def getTestSuite():

    testSuite = unittest.TestSuite()

    ''' Add the Range Ring tests '''
 
    loader = unittest.TestLoader()

    testSuite.addTest(loader.loadTestsFromTestCase(RangeRingUtilsTestCase.RangeRingUtilsTestCase))

    return testSuite
