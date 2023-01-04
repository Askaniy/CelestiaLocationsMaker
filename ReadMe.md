# Celestia locations maker (CLM)

A Python script that creates location files for Celestia in SSC format from [Gazetteer of Planetary Nomenclature](https://planetarynames.wr.usgs.gov/) database.

## How to use it?

You need Python 3.6 or higher (due to f-strings). Tested on Windows 10/11 and Linux. The script doesn't require installing additional libraries or an Internet connection because the [database](data/searchresults.csv) is preloaded.

Run [clm.py](clm.py) in console, customize settings, choose output format (and target for single file mode). Done. In case of problems, the tool will notify you.

## What do I need to know?

- CLM is still has a beta status: it may contain inaccuracies for some bodies. Help is welcome.
- It is designed for the Celestia 1.7 and Celestia Origin, which support all existing [types of locations](https://en.wikibooks.org/wiki/Celestia/SSC_File#Type_%22string%22). You can turn on legacy mode that constrains location types according to Celestia 1.6 after launch.
- By default, the script adds a file description and creation info by Celestia Origin standard to the first lines of SSC. You can turn off the feature after launch.
- By default, the script adds comments about the location type, dates of creation and last update, as well as information about the origin of the name for each location. You can turn off the feature after launch.
- Names of `albedo features (AL)`, `mare/maria (ME)`, `oceanus/oceani (OC)`, `regio/regiones (RE)` and `terra/terrae (TA)` are written in capital letters.
- Coordinates and altitude of locations can be set manually through the [custom_longlat.txt](data/custom_longlat.txt). Their parameters are tailored to the models used in Celestia Origin. Also, it contains locations with not specified coordinates.
- The [database](data/searchresults.csv) contains 333 locations with zero sizes. If the size of one of them is specified in the [custom_size.txt](data/custom_size.txt), the script uses it. Else, `Importance` sets to 20 for albedo features and `Size` sets to 10 (km) for other location types.
- The rotation of Venus, Puck, Miranda, Ariel, Umbriel, Titania, Oberon, Triton, Bennu, Ida, Itokawa, Ryugu and Steins is retrograde. For correct display in Celestia, their coordinates are inverted.
- The IAU in the location database uses the [Vesta coordinate system](https://en.wikipedia.org/wiki/4_Vesta#Coordinate_systems) with an offset of 150° relative to the *Dawn* team system. Since Celestia Origin uses the model based on the second coordinate system, this shift is hardcoded.

## How to update the database file?

1. Go to [Planetary Names: Advanced Nomenclature Search](https://planetarynames.wr.usgs.gov/AdvancedSearch);
2. Scroll, tap the `Search` button;
3. Tap `+ Add/Remove Columns` on the top of the table;
4. Check all the boxes there;
5. Scroll, choose the `CSV` link;
6. Save the file to the `data` folder.

The last database update was on January 4, 2023.
