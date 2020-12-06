# Celestia locations maker

A Python script that creates location files for Celestia in SSC format from [Gazetteer of Planetary Nomenclature](https://planetarynames.wr.usgs.gov/) database.

## How to use it?
You need Python 3.6 or higher (due to f-strings) and probably Windows. The script doesn't require an Internet connection because the [database](SearchResults) is preloaded.

Run [clm.py](clm.py), select the object and file name. Done. In case of problems, the script will notify you.

## How to update the database file?
1. Go to [Planetary Names: Advanced Nomenclature Search](https://planetarynames.wr.usgs.gov/AdvancedSearch);
2. Check all the boxes in `Columns to include`;
3. Choose `Output Format` as `TSV`;
4. Do `Search` and save the file.

## What else do I need to know?
- By default, the tool is designed for the Celestia 1.7 and Celestia Origin, which support all existing [types of locations](https://en.wikibooks.org/wiki/Celestia/SSC_File#Type_%22string%22). To create SSC for Celestia 1.6, change the value of the flag `celestia16` to `True`.
- The script tries to automatically find the main path and create the `locations` folder. If it fails, you can try specifying them manually in the code.
- Names of `ME`, `OC`, `RE` and `TA` location types are written in capital letters.
- For bodies with an unknown size, it sets to 10 km.
- The IAU in the location database uses the [Vesta coordinate system](https://en.wikipedia.org/wiki/4_Vesta#Coordinate_systems) with an offset of 150° relative to the *Dawn* team system. Since Celestia Origin uses the model based on the second coordinate system, this shift is hardcoded.

## Roadmap
- The database contains 340 locations with zero sizes. The record holders are Mercury, Venus, Mars, Rhea, Titan and Triton. I made a version of the script that displays all dimensionless locations on the maps of the corresponding bodies. I hope we can fix them.
- It is possible to create an algorithm that will determine the height of a location using an elevation map. This is important for non-ellipsoidal bodies such as Vesta.