import os
import sys
import inspect
from datetime import date
today = date.today().strftime("%d.%m.%Y")


# Customizable flags

celestia16 = False
description = True
comments = True


# Lists

sets = {
    "merc_locs.ssc": ["Mercury"],
    "venus_locs.ssc": ["Venus"],
    "moon_locs.ssc": ["Moon"],
    "mars_locs.ssc": ["Mars"],
    "marsmoons_locs.ssc": ["Phobos", "Deimos"],
    "jupitermoons_locs.ssc": ["Amalthea", "Thebe", "Io", "Europa", "Ganymede", "Callisto"],
    "saturnmoons_locs.ssc": ["Epimetheus", "Janus", "Mimas", "Enceladus", "Tethys", "Dione", "Rhea", "Titan", "Hyperion", "Iapetus", "Phoebe"],
    "uranusmoons_locs.ssc": ["Puck", "Miranda", "Ariel", "Umbriel", "Titania", "Oberon"],
    "neptunemoons_locs.ssc": ["Proteus", "Triton"],
    "dwarf_planets_locs.ssc": ["Ceres", "Pluto", "Charon"],
    "asteroids_locs.ssc": ["Vesta", "Lutetia", "Ida", "Dactyl", "Mathilde", "Eros", "Gaspra", "Steins", "Itokawa", "Bennu", "Ryugu"]
}

objects = (
    "Amalthea", "Ariel", "Bennu", "Callisto", "Ceres", "Charon", "Dactyl", "Deimos", "Dione", "Enceladus", "Epimetheus", "Eros",
    "Europa", "Ganymede", "Gaspra", "Hyperion", "Iapetus", "Ida", "Io", "Itokawa", "Janus", "Lutetia", "Mars", "Mathilde",
    "Mercury", "Mimas", "Miranda", "Moon", "Oberon", "Phobos", "Phoebe", "Pluto", "Proteus", "Puck", "Rhea", "Ryugu", "Steins",
    "Tethys", "Thebe", "Titan", "Titania", "Triton", "Umbriel", "Venus", "Vesta"
)

retrograde_rotators = (
    "Ariel", "Bennu", "Ida", "Itokawa", "Miranda", "Oberon", "Puck", "Ryugu", "Steins", "Titania", "Triton", "Umbriel", "Venus"
)

#columns = ("Feature_ID", "Feature_Name", "Clean_Feature_Name", "Target", "Diameter", "Center_Latitude", "Center_Longitude",
#    "Northern_Latitude", "Southern_Latitude", "Eastern_Longitude", "Western_Longitude", "Coordinate_System", "Continent", "Ethnicity",
#    "Feature_Type", "Feature_Type_Code", "Quad", "Approval_Status", "Approval_Date", "Reference", "Origin", "Additional_Info",
#    "Last_Updated"
#)

celestia16supports = (
    "AA", "AS", "CA", "CH", "CM", "CR", "DO", "ER", "FL", "FO", "FR", "IN", "LF", "LI", "ME", "MN", "MO", "PE", "PL", "PM", "RE", "RI",
    "RT", "RU", "TA", "TE", "TH", "UN", "VA", "XX"
)


# SSC writer

def reader(target):
    locations = []
    for line in database:
        data = dict(zip(columns, line[:-1].split("\t")))
        try:
            if target == data["Target"] and data["Approval_Status"] == "Approved":
                location = "\n"

                # Comments
                if comments:
                    if data["Approval_Date"] != "" and data["Last_Updated"] != "":
                        location += f'# Approval date: {data["Approval_Date"]}; Last update: {data["Last_Updated"]}\n'
                    if data["Origin"] != "":
                        location += f'# Origin: {data["Origin"]}\n'
                    if data["Additional_Info"] != "":
                        location += f'# Additional info: {data["Additional_Info"]}\n'
                
                # Name
                if data["Feature_Type_Code"] in ("AL", "ME", "OC", "RE", "TA"):
                    location += f'Location "{data["Feature_Name"].upper()}"'
                else:
                    location += f'Location "{data["Feature_Name"]}"'
                
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
                if data["Feature_Name"] in coord_dict:
                    location += f'\tLongLat\t[ {coord_dict[data["Feature_Name"]]} ]\n'
                else:
                    long = data["Center_Longitude"]
                    lat = data["Center_Latitude"]
                    if data["Target"] in retrograde_rotators:
                        long = long[1:] if long[0] == "-" else "-"+long
                        lat = lat[1:] if lat[0] == "-" else "-"+lat
                    elif data["Target"] == "Vesta": # coordinate system by the Dawn team, see ReadMe
                        long = round(float(data["Center_Longitude"])-150, 2)
                    location += f'\tLongLat\t[ {long} {lat} 0 ]\n'
                
                # Size/Importance
                if float(data["Diameter"]) == 0:
                    if data["Feature_Type_Code"] == "AL":
                        location += f'\tImportance\t20\n'
                    elif data["Feature_Name"] in size_dict:
                        location += f'\tSize\t{size_dict[data["Feature_Name"]]}\n'
                    else:
                        location += f'\tSize\t10\n'
                else:
                    location += f'\tSize\t{data["Diameter"]}\n'
                
                # Type
                if celestia16 and data["Feature_Type_Code"] not in celestia16supports:
                    location += f'\tType\t"XX"'
                else:
                    location += f'\tType\t"{data["Feature_Type_Code"]}"'
                if comments:
                    location += f'\t# {data["Feature_Type"]}'
                
                location += '\n}\n'
                locations.append(location)

        except KeyError:
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
if not os.path.isfile(data_path + "/SearchResults"):
    print('\n"SearchResults" not found, please try again.\n')
    sys.exit(1)

save_path = path + "/locations"
try:
    if not os.path.exists(save_path):
        os.mkdir(save_path)
except Exception:
    print('\nCan’t find or create "locations" folder, you can try to create it manually.\n')
    sys.exit(1)


# Target detection

print("\n  Welcome to Celestia Locations Maker!\n  Please choose processing mode:")
print("\nStandard object sets       Objects separately")
print("[0] Select...              [1] Select...")
print("[2] Process all            [3] Process all")
choice = input("\nEnter the number to start: ")

if choice == "0":
    temp = "\n"
    for index, item in enumerate(list(sets.keys())):
        temp += f"[{index}] {item}".ljust(26)
        if (index + 1) % 2 == 0:
            print(temp)
            temp = ""
    if temp != "":
        print(temp)
    
    try:
        set_list = [list(sets.items())[int(input("\nPlease enter the target number: "))]]
    except Exception:
        print("Input was wrong, please try again.\n")
        sys.exit(2)

elif choice == "1":
    temp = "\n"
    for index, item in enumerate(objects):
        temp += f"[{index}] {item}".ljust(16)
        if (index + 1) % 3 == 0:
            print(temp)
            temp = ""
    if temp != "":
        print(temp)
    
    try:
        set_list = [objects[int(input("\nPlease enter the target number: "))]]
    except Exception:
        print("Input was wrong, please try again.\n")
        sys.exit(2)

elif choice == "2":
    set_list = list(sets.items())

elif choice == "3":
    set_list = objects

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

with open(data_path + "/SearchResults", "r", encoding="UTF-8") as SearchResults:

    # Skip indent and define columns
    content = SearchResults.readlines()
    columns = list(map(str.strip, content[5][:-1].split("\t")))
    database = content[6:]

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
    print(f'Done\n')