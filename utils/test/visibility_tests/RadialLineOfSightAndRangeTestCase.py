# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2016-2017 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
 ==================================================
 RadialLineOfSightAndRangeTestCase.py
 --------------------------------------------------
 requirements: ArcGIS 10.3+, Python 2.7
 author: ArcGIS Solutions
 contact: support@esri.com
 company: Esri
 ==================================================
 description:
 Unit tests for Visibility tools
 ==================================================
'''

# IMPORTS ==========================================
import os
import unittest

import arcpy

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import UnitTestUtilities
import Configuration

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), \
    r"../../../toolboxes/scripts")))
import RadialLineOfSightAndRange

class RadialLineOfSightAndRangeTestCase(unittest.TestCase):

    def setUp(self):
        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''
            
        Configuration.Logger.debug('.....RadialLineOfSightAndRangeTestCase.setUp')
        arcpy.env.overwriteOutput = True 

    def tearDown(self):
        Configuration.Logger.debug(".....RadialLineOfSightAndRangeTestCase.tearDown")
        
    def test_toolboxMain(self):

        Configuration.Logger.info(".....RadialLineOfSightAndRange.test_toolboxMain")

        if arcpy.CheckExtension("3D") == "Available":
            arcpy.CheckOutExtension("3D")
        else:
            raise Exception("3D license is not available.")

        observers = os.path.join(Configuration.militaryInputDataGDB, "RLOS_Observers")
        elevationSurface = os.path.join(Configuration.militaryInputDataGDB, "ElevationUTM_Zone10")

        viewshedFC   = r'in_memory\viewshed'
        donutWedgeFC = r'in_memory\wedge'
        pieWedgeFC   = r'in_memory\fullwedge'

        RadialLineOfSightAndRange.createViewshed(observers, \
           elevationSurface, \
           '1000', '90', '180', '20', '500', \
           viewshedFC, donutWedgeFC, pieWedgeFC)

        viewshedFeaturesCount = int(arcpy.GetCount_management(viewshedFC).getOutput(0))
        donutFeaturesCount    = int(arcpy.GetCount_management(donutWedgeFC).getOutput(0))
        pieFeaturesCount      = int(arcpy.GetCount_management(pieWedgeFC).getOutput(0))

        self.assertGreater(viewshedFeaturesCount, 0, "No output features created for " + str(viewshedFC))
        self.assertGreater(donutFeaturesCount, 0, "No output features created for " + str(donutWedgeFC))
        self.assertGreater(pieFeaturesCount, 0, "No output features created for " + str(pieWedgeFC))

    def test_surfaceContainsPoint(self):
        '''
        Check if elevation dataset contains the specified point
        '''
        Configuration.Logger.info(".....RadialLineOfSightAndRange.test_surfaceContainsPoint")

        observers = os.path.join(Configuration.militaryInputDataGDB, "RLOS_Observers")

        elevationSurface = os.path.join(Configuration.militaryInputDataGDB, "ElevationUTM_Zone10")

        pointsIn = RadialLineOfSightAndRange.surfaceContainsPoints(observers, elevationSurface)

        self.assertTrue(pointsIn, 'Points not within Surface as Expected')

    def test_surfaceContainsPointWgs84(self): 
        '''
        Check if elevation dataset contains the specified point not in same SR as surface
        '''
        Configuration.Logger.info(".....RadialLineOfSightAndRange.test_surfaceContainsPointWgs84")

        # List of coordinates
        coordinates = [[-121.5, 36.5], [-121.2, 36.1]]

        # Create an in_memory feature class to contain the coordinate pairs
        observerFeatureClass = arcpy.CreateFeatureclass_management(
            "in_memory", "tempfc", "POINT", spatial_reference=arcpy.SpatialReference(4326))[0]

        # Open an insert cursor
        with arcpy.da.InsertCursor(observerFeatureClass, ["SHAPE@"]) as cursor:
            # Iterate through list of coordinates and add to cursor
            for (x, y) in coordinates:
                point = arcpy.Point(x, y)
                pointGeo = arcpy.PointGeometry(point, \
                    arcpy.SpatialReference(4326))
                cursor.insertRow([pointGeo])

        elevationSurface = os.path.join(Configuration.militaryInputDataGDB, "ElevationUTM_Zone10")

        arePointsIn = RadialLineOfSightAndRange.surfaceContainsPoints(observerFeatureClass, elevationSurface)

        self.assertTrue(arePointsIn, 'Points not within Surface as Expected')
        
if __name__ == "__main__":
    unittest.main()