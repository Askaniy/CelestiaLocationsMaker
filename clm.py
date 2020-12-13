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

files = {
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

targets = [
    "Amalthea", "Ariel", "Bennu", "Callisto", "Ceres", "Charon", "Dactyl", "Deimos", "Dione", "Enceladus", "Epimetheus", "Eros",
    "Europa", "Ganymede", "Gaspra", "Hyperion", "Iapetus", "Ida", "Io", "Itokawa", "Janus", "Lutetia", "Mars", "Mathilde",
    "Mercury", "Mimas", "Miranda", "Moon", "Oberon", "Phobos", "Phoebe", "Pluto", "Proteus", "Puck", "Rhea", "Ryugu", "Steins",
    "Tethys", "Thebe", "Titan", "Titania", "Triton", "Umbriel", "Venus", "Vesta"
]

#columns = ["Feature_ID", "Feature_Name", "Clean_Feature_Name", "Target", "Diameter", "Center_Latitude", "Center_Longitude",
#    "Northern_Latitude", "Southern_Latitude", "Eastern_Longitude", "Western_Longitude", "Coordinate_System", "Continent", "Ethnicity",
#    "Feature_Type", "Feature_Type_Code", "Quad", "Approval_Status", "Approval_Date", "Reference", "Origin", "Additional_Info",
#    "Last_Updated"
#]

celestia16supports = [
    "AA", "AS", "CA", "CH", "CM", "CR", "DO", "ER", "FL", "FO", "FR", "IN", "LF", "LI", "ME", "MN", "MO", "PE", "PL", "PM", "RE", "RI",
    "RT", "RU", "TA", "TE", "TH", "UN", "VA", "XX"
]


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
                if data["Feature_Type_Code"] in ["AL", "ME", "OC", "RE", "TA"]:
                    location += f'Location "{data["Feature_Name"].upper()}"'
                else:
                    location += f'Location "{data["Feature_Name"]}"'
                
                # Target
                if data["Target"] == "Moon":
                    location += f' "Sol/Earth/Moon"\n'
                elif data["Target"] in files["marsmoons_locs.ssc"]:
                    location += f' "Sol/Mars/{data["Target"]}"\n'
                elif data["Target"] in files["jupitermoons_locs.ssc"]:
                    location += f' "Sol/Jupiter/{data["Target"]}"\n'
                elif data["Target"] in files["saturnmoons_locs.ssc"]:
                    location += f' "Sol/Saturn/{data["Target"]}"\n'
                elif data["Target"] in files["uranusmoons_locs.ssc"]:
                    location += f' "Sol/Uranus/{data["Target"]}"\n'
                elif data["Target"] in files["neptunemoons_locs.ssc"]:
                    location += f' "Sol/Neptune/{data["Target"]}"\n'
                elif data["Target"] in ["Pluto", "Charon"]:
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
                    if data["Target"] == "Vesta":
                        location += f'\tLongLat\t[ {round(float(data["Center_Longitude"])-150, 2)} {data["Center_Latitude"]} 0 ]\n'
                    else:
                        location += f'\tLongLat\t[ {data["Center_Longitude"]} {data["Center_Latitude"]} 0 ]\n'
                
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

print("\n[0] Standard Celestia locations files\n[1] By object in the database")
choice = input("\nEnter targets list number to show it: ")

if choice == "0":
    files_list = list(files.keys())
    temp = "\n"
    for index, item in enumerate(files_list):
        temp += f"[{index}] {item}".ljust(26)
        if (index + 1) % 2 == 0:
            print(temp)
            temp = ""
    if temp != "":
        print(temp)
    
    try:
        file_name = files_list[int(input("\nPlease enter the target number: "))]
        target_list = files[file_name]
    except Exception:
        print("Input was wrong, please try again.\n")
        sys.exit(2)
    
elif choice == "1":
    temp = "\n"
    for index, item in enumerate(targets):
        temp += f"[{index}] {item}".ljust(16)
        if (index + 1) % 3 == 0:
            print(temp)
            temp = ""
    if temp != "":
        print(temp)
    
    try:
        target_list = [targets[int(input("\nPlease enter the target number: "))]]
    except Exception:
        print("Input was wrong, please try again.\n")
        sys.exit(2)
    
    print(f'\nDo you want to save the output file as "{target_list[0].lower()}_locs.ssc"?')
    file_name = input('Press "Enter" if yes, else enter custom file name: ')
    if file_name == "":
        file_name = target_list[0].lower() + "_locs.ssc"
    
else:
    print("Input was wrong, please try again.\n")
    sys.exit(2)

save_path = path + "/locations/"
print(f'\nSave path: {save_path + file_name}')


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
    with open(save_path + file_name, "w", encoding="UTF-8") as ssc:
        if len(target_list) == 1:
            locations = reader(target_list[0])
            counter = f'# {len(locations)} location{"" if len(locations) == 1 else "s"} on {target_list[0]}.\n\n'
            crutch = "\n"
        else:
            print("")
            locations = []
            n = 0
            for target in target_list:
                locs = reader(target)
                n += len(locs)
                if description:
                    locations.append(f'\n\n# {len(locs)} locations on {target}.\n')
                locations.append("".join(locs))
                print(f'{target} was done')
            target_list_temp = target_list[:-2]
            target_list_temp.append(target_list[-2]+" and "+target_list[-1])
            counter = f'# {n} locations on {", ".join(target_list_temp)}.\n\n'
            crutch = ""
        if description:
            ssc.write(counter)
            ssc.write(f'# SSC-file author: CLM tool by Askaniy.\n\n')
            ssc.write(f'# Date of creation: {today}\n')
            ssc.write(f'# Last update: {today}\n')
        ssc.write(crutch + "".join(locations))
        print(f'\nDone\n')