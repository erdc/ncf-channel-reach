# National Channel Framework ChannelReach Changelog

Developed by:  
Connor Hicks, Jaden Nobles  
Junior Software Engineers, ARA

Magdalena Asborno, PhD  
Senior Consultant, ARA  
Research Civil Engineer, USACE-ERDC

The "National Channel Framework ChannelReach Changelog" Process tracks changes between 2 versions of the National Channel Framework ChannelReach polygon layer.

First, the user selects the NCF ChannelReach versions they wish to compare, and choose the properties they want to compare between the two versions. Then, they select the .csv filepath where the data will be saved after the script finishes running. Finally, they run the Process. After execution, the .csv file is populated with all notable changes between the two NCF versions.

## Cite this work

If you use this work, please add this citation:

Asborno, M., C. Hicks, and K. N. Mitchell. 2025. Quality Control for Waterway Network ERDC/CHL CHETN-IX-##. Vicksburg, MS: US Army Engineer Research and Development Center, Coastal and Hydraulics Laboratory. DOI forthcoming

## National Channel Framework ChannelReach Changelog

### Prerequisites

1. Install QGIS ([3.34.X](https://ftp.osuosl.org/pub/osgeo/download/qgis/windows/QGIS-OSGeo4W-3.34.15-1.msi))

### How to run

1. Download the NCFChangelog.py file.
2. Open a QGIS project with the layers you wish to compare between, or add the desired layers.
3. In the top menu, click `Layer` > `Add Layer` > `Add ArcGIS REST Server Layer...`
4. Click `New`. Enter a name for this server connection.
5. The URL should point to the National Channel Framework API. Usually is [https://services7.arcgis.com/n1YM8pTrFmm7L4hs/ArcGIS/rest/services/National_Channel_Framework/FeatureServer](https://services7.arcgis.com/n1YM8pTrFmm7L4hs/ArcGIS/rest/services/National_Channel_Framework/FeatureServer).
6. Click `OK`. Click `Connect`.
7. Select the ChannelReach polygon layer. Click `Add` or `Add with Filter`.
8. Navigate to your Processing Toolbox window. If you do not see this window, in the top menu, click `Processing` and ensure that `Toolbox` is enabled.
9. Click the 2nd icon in the top row of the Processing Toolbox window > `Add Script to Toolbox...`

![Screenshot 2024-11-06 142555](https://github.com/user-attachments/assets/e22fd81c-5442-4181-a781-51129e7f53d2)

12. Navigate to your downloaded Toolbox Script file. This adds a shortcut to your QGIS installation to the Toolbox Script file for future use.
13. Scroll down the Processing Toolbox window until you see `Scripts`. Click `Scripts` > `ChannelReach` > `ChannelReach Changelog`.

![image](https://github.com/user-attachments/assets/bba900c6-d05d-429e-bc5c-e4a1afbd5ab4)

14. After clicking the Tool, a ChannelReach Changelog menu will appear for you to enter the desired parameters. The help window to the right provides additional insights behind each parameter. Below is an example screenshot of the ChannelReach Changelog menu with completed parameters as an example.

![image](https://github.com/user-attachments/assets/c31e874b-828e-4022-9926-c88ae4208ebb)

16. The first input prompts you to select the old ChannelReach layer you want to use.
17. The second input prompts you to select the unique ID field of the old ChannelReach layer.
18. The third input prompts you to select the new ChannelReach layer you want to use.
19. The fourth input prompts you to select the unique ID field of the new ChannelReach layer.
20. The fifth and sixth inputs prompt you to enter the fields from the old and new layers that you would like to compare.  
    _(Note: Both old and new fields must be the same and in identical order.)_
21. The final input labeled `Tabular Output` prompts you to specify the .csv filepath where you would like the data to output after the Process has finished running. All parameters except the `Geospatial Output` are required.
22. Once all fields are filled out, click `Run` in the bottom right hand corner.
23. When the script is finished running, the log should look similar to the figure below, and the progress bar at the bottom will say `Complete`.

![image](https://github.com/user-attachments/assets/e8fddd7a-be9c-49d6-98cb-58d5a88e1ba6)

### How to read the .csv Tabular Output file

The `Tabular Output` will be written into a .csv file. The .csv file will only contain data for the ChannelReaches that have been added, removed, or changed.

- The left column will have the unique ID `ChannelReachIDPK` field that have been affected.
- The column titled `District` will have the district that the ChannelReach is a part of.
- The column title `Type` contains information on the whether a ChannelReach was added, removed, or changed. If data was changed, it will specify which fields were changed.  
  _(Note: The Shape\_\_Area fields will only be reported as changed if the absolute difference in areas of a ChannelReach's geometries is greater than 0.0000001 square miles.)_

![image](https://github.com/user-attachments/assets/ec5cb259-da1a-4a16-bcf3-805509214494)

Below is an example screenshot of a .csv file displaying both the old and new data fields for comparison.

![image](https://github.com/user-attachments/assets/e517acb0-7323-4d9f-84bd-bc9b1dca1b2f)

### How to read the Geospatial Output layer

The `Geospatial Output` will added to your Layers in the QGIS project, either as a temporary layer or in the file specified by the user. The `Geospatial Output` contains the same data as the `Tabular Output`, with the addition of two new columns and geometries for the ChannelReaches.

- The column titled `GeometrySource` contains information about the entry's geometry origins.
  - If a ChannelReachIDPK's Shape\_\_Area is reported as changed, two entries and geometries are displayed: one displays geometry from the old ChannelReach layer, the other displays geometry from the new ChannelReach layer.
  - If a ChannelReachIDPK is reported as removed, geometry from the old ChannelReach layer is displayed.
  - Otherwise, geometry from the new ChannelReach layer is displayed for a ChannelReachIDPK.
- The column titled `ID` is a unique ID field to differentiate between GeometrySources of "New" & "Old" between the same ChannelReachIDPK entry.

Below is an example screenshot of a the `Geospatial Output` layer displaying the geometry of a removed ChannelReach. Notice how the old ChannelReach polygons are a red outline, the new ChannelReach polygons are a blue outline, and the brown `Geospatial Output` polygons intersect areas where a red polygon is present without a matching blue polygon.

![image](https://github.com/user-attachments/assets/0fbfbd06-386f-47f3-a2bd-493ef3ef6d93)
