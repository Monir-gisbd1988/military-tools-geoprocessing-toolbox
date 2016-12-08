# coding: utf-8
'''
------------------------------------------------------------------------------
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
------------------------------------------------------------------------------
 ==================================================
 Military_Tools.pyt
 --------------------------------------------------
 requirements: ArcGIS X.X, Python 2.7 or Python 3.4
 author: ArcGIS Solutions
 contact: ArcGISTeam<Solution>@esri.com
 company: Esri
 ==================================================
 description: <Description>
 ==================================================
 history:
 12/07/2016 - mf - Converting standard TBX to PYT
 ==================================================
'''

# IMPORTS ==========================================
import os
import sys
import traceback
import arcpy
import imp
from arcpy import env
from scripts import ConvertCoordinates

class Toolbox(object):
    def __init__(self):
        """
        Define the toolbox (the name of the toolbox is the name of the
        .pyt file).
        """
        self.label = "Military Tools"
        self.alias = "mt"

        # List of tool classes associated with this toolbox
        self.tools = [ConvertCoordinatesTool]

class MilToolsUtils(object):
    '''
    Support class for military tools.
    Includes commonly used units and types.
    '''
    def __init__(self):
        '''
        '''
        self.coordinateNotations = ["DD_1", "DD_2",
                                    "DDM_1", "DDM_2",
                                    "DMS_1", "DMS_2",
                                    "GARS", "GEOREF",
                                    "UTM_BANDS", "UTM_ZONES",
                                    "USNG", "MGRS"]
        self.doubleFieldCoordinateNotations = ["DD_2", "DDM_2", "DMS_2"]
        self.linearUnits = ["METER", "KILOMETER", "MILES", "NAUTICAL_MILES", "FEET", "US_SURVEY_FEET"]
        self.angularUnits = ["DEGREES", "MILS", "RADS", "GRADS"]
        self.lineTypes = ["GEODESIC", "GREAT_CIRCLE", "RHUMB_LINE", "NORMAL_SECTION"]
        self.srGCS_WGS_1984 = arcpy.SpatialReference(4326)
    

# <tool> ===========================================
class ConvertCoordinatesTool(object):
    '''
    inputTable - input table, each row will be a separate line feature in output
    inputCoordinateFormat - coordinate notation format of input vertices
    inputXField - field in inputTable for vertex x-coordinate, or full coordinate
    inputYField - field in inputTable for vertex y-coordinate, or None
    outputTable -  output table containing converted coordinate notations
    inputSpatialReference - spatial reference of input coordinates
    
    returns table
    
    inputCoordinateFormat must be one of the following:
    •	DD_1: Both longitude and latitude values are in a single field. Two values are separated by a space, a comma, or a slash.
    •	DD_2: Longitude and latitude values are in two separate fields.
    •	DDM_1: Both longitude and latitude values are in a single field. Two values are separated by a space, a comma, or a slash.
    •	DDM_2: Longitude and latitude values are in two separate fields.
    •	DMS_1: Both longitude and latitude values are in a single field. Two values are separated by a space, a comma, or a slash.
    •	DMS_2: Longitude and latitude values are in two separate fields.
    •	GARS: Global Area Reference System. Based on latitude and longitude, it divides and subdivides the world into cells.
    •	GEOREF: World Geographic Reference System. A grid-based system that divides the world into 15-degree quadrangles and then subdivides into smaller quadrangles.
    •	UTM_ZONES: The letter N or S after the UTM zone number designates only North or South hemisphere.
    •	UTM_BANDS: The letter after the UTM zone number designates one of the 20 latitude bands. N or S does not designate a hemisphere.
    •	USNG: United States National Grid. Almost exactly the same as MGRS but uses North American Datum 1983 (NAD83) as its datum.
    •	MGRS: Military Grid Reference System. Follows the UTM coordinates and divides the world into 6-degree longitude and 20 latitude bands, but MGRS then further subdivides the grid zones into smaller 100,000-meter grids. These 100,000-meter grids are then divided into 10,000-meter, 1,000-meter, 100-meter, 10-meter, and 1-meter grids.
    •	SHAPE: Only available when a point feature layer is selected as input. The coordinates of each point are used to define the output format
    '''
    import MilToolsUtils
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ConvertCoordinates"
        self.description = "Converts source coordinates in a table \
                           to multiple coordinate formats.  This tool \
                           uses an input table with coordinates and \
                           outputs a new table with fields for the following \
                           coordinate formats: Decimal Degrees, Decimal \
                           Degrees Minutes, Degrees Minutes Seconds, \
                           Universal Transverse Mercator, Military Grid \
                           Reference System, U.S. National Grid, \
                           Global Area Reference System, and \
                           World Geographic Reference System"
        self.canRunInBackground = False
        self.category = "Conversion"
        mtu = MilToolsUtils()
        

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        param0 = arcpy.Parameter(
            displayName="Input Table",
            name="inputTable",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input"
        )
        
        param1 = arcpy.Parameter(
            displayName="Input Coordinate Format",
            name="inputCoordinateFormat",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param1.filters[1].type = "ValueList"
        param1.filters[1].list = self.mtu.coordinateNotations
        param1.value = "DD_2"
        
        param2 = arcpy.Parameter(
            displayName="X Field (longitude, UTM, MGRS, USNG, GARS, GEOREF)",
            name="inputXField",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        param2.parameterDependencies[param0]
        
        param3 = arcpy.Parameter(
            displayName="Y Field (latitude)",
            name="inputYField",
            datatype="Field",
            parameterType="Optional",
            direction="Input"
        )
        param3.parameterDependencies[param0]
        
        param4 = arcpy.Parameter(
            displayName="Output Table",
            name="outputTable",
            datatype="DETable",
            parameterType="Required",
            direction="Output"
        )
        param4.value="%scratchGDB%/convertCoords"
        param4.schema.clone = True
        f = []
        for fN in ["DDLat", "DDLon", "DDMLat", "DDMLon", "DMSLat", "DMSLon", "MGRS", "USNG", "GARS", "GEOREF"]:
            a = arcpy.Field()
            a.name = fN
            a.type = "String"
            f.append(a)
        param4.schema.additionalFields[f]
        
        param5 = arcpy.Parameter(
            displayName="Spatial Reference",
            name="inputSpatialReference",
            datatype="GPSpatialReference",
            parameterType="Optional",
            direction="Input"
        )
        param5.value = self.mtu.srGCS_WGS_1984.exportToString()
        
        params = [param0, param1, param2, param3, param4, param5]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        #0 - Input Table
        #1 - Input Coordinate Format
        if parameters[1].altered:
          if not parameters[1].value in self.mtu.doubleFieldCoordinateNotations:
            parameters[3].value = parameters[2].value
            parameters[3].enabled = False
          else:
            parameters[3].enabled = True
        #2 - X Field
        #3 - Y Field
        #4 - Output Table
        #5 - Spatial Reference
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        #0 - Input Table
        #1 - Input Coordinate Format
        #2 - X Field
        #3 - Y Field
        if parameters[1].value in self.mtu.doubleFieldCoordinateNotations:
          if parameters[3].value == None or parameters[3].value == "":
            parameters[3].setErrorMessage("Coordinate formats 'DD_2', 'DDM_2', and 'DMS_2' require both X Field and Y Field from the input table.")
        #4 - Output Table
        #5 - Spatial Reference
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        deleteme = [] # intermediate datasets to be deleted
        debug = True # extra messaging during development
        try:
            # get/set environment
            env.overwriteOutput = True

            # Add execution code
            ConvertCoordinates.convertCoordinates(parameters[0],
                                                  parameters[1],
                                                  parameters[2],
                                                  parameters[3],
                                                  parameters[4],
                                                  parameters[5])

            # Set output
            arcpy.SetParameter(4, outputTable)

        except arcpy.ExecuteError:
            # Get the tool error messages
            msgs = arcpy.GetMessages()
            arcpy.AddError(msgs)
            print(msgs)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            # Return python error messages for use in script tool or Python Window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

        finally:
            if debug is False and len(deleteme) > 0:
                # cleanup intermediate datasets
                if debug is True: arcpy.AddMessage("Removing intermediate datasets...")
                for i in deleteme:
                    if debug is True: arcpy.AddMessage("Removing: " + str(i))
                    arcpy.Delete_management(i)
                if debug is True: arcpy.AddMessage("Done")
        return