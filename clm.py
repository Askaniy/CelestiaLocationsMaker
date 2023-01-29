import os
import sys
import csv
import inspect
from math import ceil
from datetime import date
today = date.today().strftime("%d.%m.%Y")


# Lists

sets = {
    "merc_locs.ssc": ["Mercury"],
    "venus_locs.ssc": ["Venus"],
    "moon_locs.ssc": ["Moon"],
    "mars_locs.ssc": ["Mars"],
    "marsmoons_locs.ssc": ["Phobos", "Deimos"],
    "jupitermoons_locs.ssc": ["Amalthea", "Thebe", "Io", "Europa", "Ganymede", "Callisto"],
    "saturnmoons_locs.ssc": [
        "Epimetheus", "Janus", "Mimas", "Enceladus", "Tethys", "Dione", "Rhea", "Titan", "Hyperion", "Iapetus", "Phoebe"
    ],
    "uranusmoons_locs.ssc": ["Puck", "Miranda", "Ariel", "Umbriel", "Titania", "Oberon"],
    "neptunemoons_locs.ssc": ["Proteus", "Triton"],
    "dwarfplanets_locs.ssc": ["Ceres", "Pluto", "Charon"],
    "asteroids_locs.ssc": [
        "Vesta", "Lutetia", "Ida", "Dactyl", "Mathilde", "Eros", "Gaspra", "Steins", "Itokawa", "Bennu", "Ryugu"
    ]
}

objects = tuple(sorted(sum(sets.values(), [])))

retrograde_rotators = (
    "Ariel", "Bennu", "Ida", "Itokawa", "Miranda", "Oberon", "Puck", "Ryugu", "Steins", "Titania", "Triton", "Umbriel", "Venus"
)

#columns = (
#   'Feature ID', 'Feature Name', 'Clean Feature Name', 'Target', 'Diameter', 'Center Latitude', 'Center Longitude',
#   'Northernmost Latitude', 'Southernmost Latitude', 'Easternmost Longitude', 'Westernmost Longitude', 'Coordinate System',
#   'Continent Ethnicity', 'Feature Type', 'Feature Type Code', 'Quad', 'Approval Status', 'Approval Date', 'Reference',
#   'Origin', 'Additional Info', 'Last Updated'
#)

celestia16supports = (
    "AA", "AS", "CA", "CH", "CM", "CR", "DO", "ER", "FL", "FO", "FR", "IN", "LF", "LI", "ME", "MN", "MO", "PE", "PL", "PM",
    "RE", "RI", "RT", "RU", "TA", "TE", "TH", "UN", "VA", "XX"
)

none_list = ("", None, "None")
yes_list = ("y", "t", "1")
no_list = ("n", "f", "0")


# SSC writer

def reader(target):
    global zero_size_counter
    locations = []
    for line in database:
        data = dict(zip(columns, line))
        if target == data["Target"] and data["Approval Status"] == "Approved":
            location = "\n"

            # Comments
            if comments:
                if data["Approval Date"] not in none_list and data["Last Updated"] not in none_list:
                    location += f'# Approval date: {data["Approval Date"]}; Last update: {data["Last Updated"]}\n'
                if data["Origin"] not in none_list:
                    location += f'# Origin: {data["Origin"]}\n'
                if data["Additional Info"] not in none_list:
                    location += f'# Additional info: {data["Additional Info"]}\n'
            
            # Name
            if data["Feature Type Code"] in ("AL", "ME", "OC", "RE", "TA"):
                location += f'Location "{data["Feature Name"].upper()}"'
            else:
                location += f'Location "{data["Feature Name"]}"'
            
            # Target
            if data["Target"] == "Moon":
                location += f' "Sol/Earth/Moon"\n'
            elif data["Target"] in sets["marsmoons_locs.ssc"]:
                location += f' "Sol/Mars/{data["Target"]}"\n'
            elif data["Target"] in sets["jupitermoons_locs.ssc"]:
                location += f' "Sol/Jupiter/{data["Target"]}"\n'
            elif data["Target"] in sets["saturnmoons_locs.ssc"]:
                location += f' "Sol/Saturn/{data["Target"]}"\n'
            elif data["Target"] in sets["uranusmoons_locs.ssc"]:
                location += f' "Sol/Uranus/{data["Target"]}"\n'
            elif data["Target"] in sets["neptunemoons_locs.ssc"]:
                location += f' "Sol/Neptune/{data["Target"]}"\n'
            elif data["Target"] in ("Pluto", "Charon"):
                location += f' "Sol/Pluto-Charon/{data["Target"]}"\n'
            elif data["Target"] == "Dactyl":
                location += f' "Sol/Ida/Dactyl"\n'
            else:
                location += f' "Sol/{data["Target"]}"\n'
            
            # LongLat
            location += '{\n'
            if data["Feature Name"] in coord_dict:
                location += f'\tLongLat\t[ {coord_dict[data["Feature Name"]]} ]\n'
            else:
                long = data["Center Longitude"]
                lat = data["Center Latitude"]
                if data["Target"] in retrograde_rotators:
                    long = long[1:] if long[0] == "-" else "-"+long
                    lat = lat[1:] if lat[0] == "-" else "-"+lat
                elif data["Target"] == "Vesta": # coordinate system by the Dawn team, see ReadMe
                    long = round(float(data["Center Longitude"])-150, 2)
                location += f'\tLongLat\t[ {long} {lat} 0 ]\n'
            
            # Size/Importance
            if float(data["Diameter"]) == 0:
                zero_size_counter += 1
                if data["Feature Type Code"] == "AL":
                    location += f'\tImportance\t20\n'
                elif data["Feature Name"] in size_dict:
                    location += f'\tSize\t{size_dict[data["Feature Name"]]}\n'
                else:
                    location += f'\tSize\t10\n'
            else:
                location += f'\tSize\t{data["Diameter"]}\n'
            
            # Type
            if celestia16 and data["Feature Type Code"] not in celestia16supports:
                location += f'\tType\t"XX"'
            else:
                location += f'\tType\t"{data["Feature Type Code"]}"'
            if comments:
                location += f'\t# {data["Feature Type"]}'
            
            location += '\n}\n'
            locations.append(location)
        
    return locations

def writer(target_list, path):
    with open(path, "w", encoding="UTF-8") as ssc:
        if len(target_list) == 1:
            target = target_list[0]
            locations = reader(target)
            print(f'{target} was processed')
            counter = f'# {len(locations)} location{"" if len(locations) == 1 else "s"} on {target}.\n\n'
            crutch = "\n"
        else:
            locations = []
            n = 0
            for target in target_list:
                locs = reader(target)
                n += len(locs)
                if description:
                    locations.append(f'\n\n# {len(locs)} locations on {target}.\n')
                locations.append("".join(locs))
                print(f'{target} was processed')
            target_list_temp = target_list[:-2]
            target_list_temp.append(f'{target_list[-2]} and {target_list[-1]}')
            counter = f'# {n} locations on {", ".join(target_list_temp)}.\n\n'
            crutch = ""
        if description:
            ssc.write(counter)
            ssc.write(f'# SSC-file author: CLM tool by Askaniy (https://github.com/Askaniy/CelestiaLocationsMaker)\n\n')
            ssc.write(f'# Date of creation: {today}\n')
            ssc.write(f'# Last update: {today}\n')
        ssc.write(crutch + "".join(locations))


# Paths detection

def folder(follow_symlinks=True): # Automatic (by jfs)
    if getattr(sys, "frozen", False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(folder)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname("/".join(path.split("\\")))

try:
    path = folder()
except Exception:
    print("Automatic folder detection failed.")
    path = input('\nPlease enter the folder where "clm.py" is located: ')

data_path = path + "/data"
if not os.path.isfile(data_path + "/searchresults.csv"):
    print('\n"searchresults.csv" not found, please try again.\n')
    sys.exit(1)

save_path = path + "/locations"
try:
    if not os.path.exists(save_path):
        os.mkdir(save_path)
except Exception:
    print('\nCan’t find or create "locations" folder, you can try to create it manually.\n')
    sys.exit(1)



print("\n                     Welcome to Celestia Locations Maker!")
print("              First come settings, then the selection of targets.\n")


# Setting flags

# by default
celestia16 = False
description = True
comments = True

if input("(1/3) Do you want to constrain location types according to Celestia 1.6? [y/n] (n): ").strip().lower() in yes_list:
    celestia16 = True
if input("(2/3) Do you want to add a file description to the first lines of SSC? [y/n] (y): ").strip().lower() in no_list:
    description = False
if input("(3/3) Do you want to add comments to SSC about each location? [y/n] (y): ").strip().lower() in no_list:
    comments = False


# Target selection

print("\n[1] Create SSC for each object    [3] Create SSCs according to standard object sets")
print("[2] Select object...              [4] Select set...")

choice = input("\nPlease choose processing mode: ")

if choice == "1":
    set_list = objects

elif choice == "2":
    table = "\n"
    worklist = objects
    col_len = ceil(len(worklist) / 3)
    columns = [worklist[0:col_len], worklist[col_len:2*col_len], worklist[2*col_len:]]
    for i in range(col_len):
        table += f'[{i+1          }] {columns[0][i]}'.ljust(20)
        table += f'[{i+1 + col_len}] {columns[1][i]}'.ljust(20)
        table += f'[{i+1+2*col_len}] {columns[2][i]}\n' if i < len(columns[2]) else "\n"
    print(table)
    
    try:
        set_list = [worklist[int(input("Please enter the target number: ")) - 1]]
    except Exception:
        print("Input was wrong, please try again.\n")
        sys.exit(2)

elif choice == "3":
    set_list = list(sets.items())

elif choice == "4":
    table = "\n"
    worklist = list(sets.keys())
    col_len = ceil(len(worklist) / 2)
    columns = [worklist[0:col_len], worklist[col_len:]]
    for i in range(col_len):
        table += f'[{i+1        }] {columns[0][i]}'.ljust(30)
        table += f'[{i+1+col_len}] {columns[1][i]}\n' if i < len(columns[1]) else "\n"
    print(table)
    
    try:
        set_list = [list(sets.items())[int(input("Please enter the target number: ")) - 1]]
    except Exception:
        print("Input was wrong, please try again.\n")
        sys.exit(2)

else:
    print("Input was wrong, please try again.\n")
    sys.exit(2)


# Custom coordinates and altitudes

coord_dict = {}
try:
    with open(data_path + "/custom_longlat.txt", "r", encoding="UTF-8") as coords:
        for line in coords:
            try:
                name, coord = line.split("\t")
                coord_dict.update({name: coord[:-1]})
            except Exception:
                pass
except Exception:
    pass


# Sizes of zero-sized locations

size_dict = {}
try:
    with open(data_path + "/custom_size.txt", "r", encoding="UTF-8") as zeros:
        for line in zeros:
            try:
                name, size = line.split("\t")
                size_dict.update({name: size[:-1]})
            except Exception:
                pass
except Exception:
    pass


# Database reader and export

zero_size_counter = 0
with open(data_path + "/searchresults.csv", "r", encoding="UTF-8") as SearchResults:
    content = list(csv.reader(SearchResults))
    columns = content[0]
    database = content[1:]

    # Output file creation
    print("")
    for set_contains in set_list:
        if type(set_contains) is tuple:
            obj_list = set_contains[1]
            save_path = f'{path}/locations/{set_contains[0]}'
        elif type(set_contains) is str:
            obj_list = [set_contains]
            save_path = f'{path}/locations/{set_contains.lower()}_locs.ssc'
        writer(obj_list, save_path)
        print(f'Saved: {save_path}\n')
    print(f'Done!\n')
    #print("Zero sized locations: ", zero_size_counter)