# Celestia locations maker (CLM)
A Python script that creates location files for Celestia in SSC format from [Gazetteer of Planetary Nomenclature](https://planetarynames.wr.usgs.gov/) database.

## How to use it?
You need Python 3.6 or higher (due to f-strings) and probably Windows (not tested on other platforms). The script doesn't require installing additional libraries or an Internet connection because the [database](data/SearchResults) is preloaded.

Run [clm.py](clm.py), select output type and target (if you selected single file mode). Done. In case of problems, the tool will notify you.

## What do I need to know?
- The tool is designed for the Celestia 1.7 and Celestia Origin, which support all existing [types of locations](https://en.wikibooks.org/wiki/Celestia/SSC_File#Type_%22string%22). To create SSC for Celestia 1.6, set the `celestia16` flag in [clm.py](clm.py) to `True`.
- By default, the script adds a file description and creation info by Celestia Origin standard to the first lines of SSC. To disable this feature, set the `description` flag to `False`.
- By default, the script adds comments about the location type, dates of creation and last update, as well as information about the origin of the name for each location. To disable this feature, set the `comments` flag to `False`.
- Names of `albedo features (AL)`, `mare/maria (ME)`, `oceanus/oceani (OC)`, `regio/regiones (RE)` and `terra/terrae (TA)` are written in capital letters.
- Coordinates and altitude of locations can be set manually through the [custom_longlat.txt](data/custom_longlat.txt). Their parameters are tailored to the models used in Celestia Origin. Also, it contains locations with not specified coordinates.
- The [database](data/SearchResults) contains 333 locations with zero sizes. If the size of one of them is specified in the [custom_size.txt](data/custom_size.txt), the script uses it. Else, `Importance` sets to 20 for albedo features and `Size` sets to 10 (km) for other location types.
- The rotation of Bennu, Ida, Itokawa, Ryugu, Steins, Triton and Venus is retrograde. For correct display in Celestia, their coordinates are inverted.
- The IAU in the location database uses the [Vesta coordinate system](https://en.wikipedia.org/wiki/4_Vesta#Coordinate_systems) with an offset of 150° relative to the *Dawn* team system. Since Celestia Origin uses the model based on the second coordinate system, this shift is hardcoded.

## How to update the database file?
1. Go to [Planetary Names: Advanced Nomenclature Search](https://planetarynames.wr.usgs.gov/AdvancedSearch);
2. Check all the boxes in `Columns to include`;
3. Choose `Output Format` as `TSV`;
4. Do `Search` and save the file.

The last update was on July 17, 2021.