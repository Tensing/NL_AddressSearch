#***************************************************************************************************************************************
#  Naam:    PostcodeHuisnummerZoeker.pyt
#  Auteur:  Egge-Jan Pollé - Tensing - ejpolle@tensing.com
#  Datum:   12 februari 2017
#***************************************************************************************************************************************
import arcpy, re, json

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Zoek op Postcode en Huisnummer"
        self.alias = "Zoek op Postcode en Huisnummer"

        # List of tool classes associated with this toolbox
        self.tools = [ZoekOpPostcodeEnHuisnummer]

class ZoekOpPostcodeEnHuisnummer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Zoek op Postcode en Huisnummer"
        self.description = "Zoek op Postcode en Huisnummer"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        pc = arcpy.Parameter(
            displayName="Postcode",
            name="in_pc",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        hnr = arcpy.Parameter(
            displayName="Huisnummer",
            name="in_hnr",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        hlt = arcpy.Parameter(
            displayName="Huisletter",
            name="in_hlt",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        htv = arcpy.Parameter(
            displayName="Toevoeging",
            name="in_htv",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        zoom = arcpy.Parameter(
            displayName="Zoomniveau",
            name="in_zoom",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        zoom.filter.type = "ValueList"
        zoom.filter.list = [100, 500, 1000, 2000]
        zoom.value = 1000
        
        return [pc,hnr,hlt,htv,zoom]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[0].value:
            postalCode = parameters[0].valueAsText.upper().replace(" ", "")
            parameters[0].value = postalCode
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        if parameters[0].value:
            postalCode = parameters[0].valueAsText
            if not re.match('[1-9]{1}[0-9]{3}[a-zA-Z]{2}$', postalCode):
                parameters[0].setErrorMessage("Onjuiste postcode. Gebruik het patroon 1234AB")
            else:
                parameters[0].clearMessage()
        if parameters[1].value:
            houseNumber = parameters[1].valueAsText
            if not re.match('[1-9]{1}[0-9]*$', houseNumber):
                parameters[1].setErrorMessage("Onjuist huisnummer. Gebruik alleen cijfers (zonder eventuele toevoeging).")
            else:
                parameters[1].clearMessage()
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        postalCode = parameters[0].valueAsText
        houseNumber = parameters[1].valueAsText
        houseLetter = parameters[2].valueAsText
        houseAddition = parameters[3].valueAsText
        zoomLevel = parameters[4].valueAsText

        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        sRName = df.spatialReference.name
        if sRName != "RD_New":
            arcpy.AddError("Kaart in onjuist coordinaatsysteem: {}".format(sRName))
            arcpy.AddError("Zoekfunctie werkt alleen voor Nederland met kaart in RD_New (EPSG:28992)")
            arcpy.AddError("Zoeken afgebroken")
            return

        houseIndication = "{}".format(houseNumber)

        queryString = "postcode='{}'  and huisnummer={}".format(postalCode,houseNumber)
        if houseLetter is None:
            queryString += " and huisletter is null"
        else:
            queryString += " and huisletter='{}'".format(houseLetter)
            houseIndication += "{}".format(houseLetter)
        if houseAddition is None:
            queryString += " and huisnummertoevoeging is null"
        else:
            queryString += " and huisnummertoevoeging='{}'".format(houseAddition)
            houseIndication += " {}".format(houseAddition)

        arcpy.AddMessage("Zoeken coördinaten voor: {} {}".format(postalCode,houseIndication))

        url = "http://basisregistraties.arcgisonline.nl/arcgis/rest/services/BAG/BAG/MapServer/0/query?where={}&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=true&f=pjson".format(queryString)

        fs = arcpy.FeatureSet()

        fs.load(url)
        desc = arcpy.Describe(fs)
        jsonResponse = json.loads(desc.pjson)

        if (len(jsonResponse['features']) == 0):
            arcpy.AddError("Geen resultaat gevonden")
            return
        else:
            streetName = jsonResponse["features"][0]["attributes"]["openbareruimtenaam"]
            locality = jsonResponse["features"][0]["attributes"]["woonplaatsnaam"]
            arcpy.AddMessage("Gevonden adres:")
            arcpy.AddMessage("{} {}".format(streetName,houseIndication))
            arcpy.AddMessage("{} {}".format(postalCode,locality))
            arcpy.AddMessage("Inzoomen naar adres...")
            xcoord = jsonResponse['features'][0]['geometry']['x']
            ycoord = jsonResponse['features'][0]['geometry']['y']
            ext = arcpy.Extent(xcoord - 200, ycoord -200, xcoord + 200, ycoord + 200)
            df.scale = float(zoomLevel)
            df.panToExtent(ext)
            arcpy.RefreshActiveView()

        return