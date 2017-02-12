# NL_AddressSearch

## Python Toolbox PostcodeHuisnummerZoeker.pyt (ArcMap 10.x)

The search functionaliuty in this toolbox uses an ArcGIS Map Service hosted by Esri Nederland:
[http://basisregistraties.arcgisonline.nl/arcgis/rest/services/BAG/BAG/MapServer](http://basisregistraties.arcgisonline.nl/arcgis/rest/services/BAG/BAG/MapServer)

Please read - and agree to - the [Esri Nederland Terms of Use](http://www.esri.nl/overig/terms-of-use) before using this toolbbox.

Each address in the Netherlands is identified by a unique combination consisting of a postal code and a house number.

The X and Y coordinates returned by the Map Service are in EPSG:28992, hence the limitation that the tool will only work when the Coordinate System of the map is set to RD_New.

The dialog and the help documentation are in Dutch.

The tool has been developed and tested using ArcMap 10.1 and ArcMap 10.3.

To use the toolbox in ArcMap: copy the *.pyt file, including the 2 corresponding *.xml files, to a folder of your choice and open it from the Catalog window in ArcMap.

![alt text](https://github.com/Tensing/NL_AddressSearch/blob/master/image/ZoekopPostcodeenHuisnummer.png "The tool's dialog box")