import os
import sys
import inspect
from datetime import date


# Customizable flags

comments = True
celestia16 = False


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
    path = input('Please enter the folder where "SearchResults" is located: ')

open_path = path + "/SearchResults"
if not os.path.isfile(open_path):
    print('"SearchResults" not found, please try again.')
    sys.exit()

try:
    if not os.path.exists(path + "/locations"):
        os.mkdir(path + "/locations")
except Exception:
    print('Can’t find or create "/locations" folder, you can try to create it manually.')
    sys.exit()


# Target detection

targets = [
    "Amalthea", "Ariel", "Bennu", "Callisto", "Ceres", "Charon", "Dactyl", "Deimos", "Dione", "Enceladus", "Epimetheus", "Eros",
    "Europa", "Ganymede", "Gaspra", "Hyperion", "Iapetus", "Ida", "Io", "Itokawa", "Janus", "Lutetia", "Mars", "Mathilde",
    "Mercury", "Mimas", "Miranda", "Moon", "Oberon", "Phobos", "Phoebe", "Pluto", "Proteus", "Puck", "Rhea", "Ryugu", "Steins",
    "Tethys", "Thebe", "Titan", "Titania", "Triton", "Umbriel", "Venus", "Vesta"
]

temp = "\n"
for index, item in enumerate(targets):
    temp += f"[{index}] {item}".ljust(8) + "\t"
    if (index + 1) % 3 == 0:
        print(temp)
        temp = ""
if temp != "":
    print(temp)

try:
    target = targets[int(input("\nPlease enter the target number: "))]
except Exception:
    print("Input was wrong, please try again.\n")
    sys.exit()

print(f'\nDo you want to save the output file as "{target.lower()}_locs.ssc"?')
name = input('Press "Enter" if yes, else enter custom file name: ')
if name == "":
    name = target.lower() + "_locs.ssc"
save_path = path + "/locations/" + name
print(f'\nSave path: {save_path}')


# Reader and writer

celestia16supports = [
    "AA", "AS", "CA", "CH", "CM", "CR", "DO", "ER", "FL", "FO", "FR", "IN", "LF", "LI", "ME", "MN", "MO", "PE", "PL", "PM", "RE", "RI",
    "RT", "RU", "TA", "TE", "TH", "UN", "VA", "XX"
]

#columns = ["Feature_ID", "Feature_Name", "Clean_Feature_Name", "Target", "Diameter", "Center_Latitude", "Center_Longitude",
#    "Northern_Latitude", "Southern_Latitude", "Eastern_Longitude", "Western_Longitude", "Coordinate_System", "Continent", "Ethnicity",
#    "Feature_Type", "Feature_Type_Code", "Quad", "Approval_Status", "Approval_Date", "Reference", "Origin", "Additional_Info",
#    "Last_Updated"
#]

with open(open_path, "r", encoding="UTF-8") as database:

    # Skip indent and define columns
    for _ in range(5):
        next(database)
    columns = list(map(str.strip, database.readline()[:-1].split("\t")))

    # Output file creation
    with open(save_path, "w", encoding="UTF-8") as ssc:

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
                    elif data["Target"] in ["Phobos", "Deimos"]:
                        location += f' "Sol/Mars/{data["Target"]}"\n'
                    elif data["Target"] in ["Amalthea", "Thebe", "Io", "Europa", "Ganymede", "Callisto"]:
                        location += f' "Sol/Jupiter/{data["Target"]}"\n'
                    elif data["Target"] in ["Dione", "Enceladus", "Epimetheus", "Hyperion", "Iapetus", "Janus", "Mimas", "Phoebe", "Rhea", "Tethys", "Titan"]:
                        location += f' "Sol/Saturn/{data["Target"]}"\n'
                    elif data["Target"] in ["Ariel", "Miranda", "Oberon", "Puck", "Titania", "Umbriel"]:
                        location += f' "Sol/Uranus/{data["Target"]}"\n'
                    elif data["Target"] in ["Proteus", "Triton"]:
                        location += f' "Sol/Neptune/{data["Target"]}"\n'
                    elif data["Target"] in ["Pluto", "Charon"]:
                        location += f' "Sol/Pluto-Charon/{data["Target"]}"\n'
                    elif data["Target"] == "Dactyl":
                        location += f' "Sol/Ida/Dactyl"\n'
                    else:
                        location += f' "Sol/{data["Target"]}"\n'
                    
                    # LongLat
                    location += '{\n'
                    if data["Target"] == "Vesta":
                        location += f'\tLongLat\t[ {float(data["Center_Longitude"])-150} {data["Center_Latitude"]} 0 ]\n'
                    else:
                        location += f'\tLongLat\t[ {data["Center_Longitude"]} {data["Center_Latitude"]} 0 ]\n'
                    
                    # Size/Importance
                    if float(data["Diameter"]) == 0:
                        if data["Feature_Type_Code"] == "AL":
                            location += f'\tImportance\t20\n'
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
                today = date.today().strftime("%d.%m.%Y")
                ssc.write(f'# {len(locations)} locations of {target}.\n\n')
                ssc.write(f'# SSC-file author: CLM tool by Askaniy.\n\n')
                #if target in ["Mercury", "Venus", "Mars", "Rhea", "Puck", "Triton"]:
                #    ssc.write(f'# SSC-file authors: CLM tool by Askaniy, Art Blos.\n\n')
                #else:
                #    ssc.write(f'# SSC-file author: CLM tool by Askaniy.\n\n')
                ssc.write(f'# Date of creation: {today}\n')
                ssc.write(f'# Last update: {today}\n\n')
                ssc.write("".join(locations))
                print("Done!\n")
                break