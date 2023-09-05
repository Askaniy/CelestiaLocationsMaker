import os
import sys
import csv
import inspect
from math import ceil
from datetime import date
today = date.today().strftime('%d.%m.%Y')


# Lists

sets = {
    'merc_locs.ssc': ['Mercury'],
    'venus_locs.ssc': ['Venus'],
    'moon_locs.ssc': ['Moon'],
    'mars_locs.ssc': ['Mars'],
    'marsmoons_locs.ssc': ['Phobos', 'Deimos'],
    'jupitermoons_locs.ssc': ['Amalthea', 'Thebe', 'Io', 'Europa', 'Ganymede', 'Callisto'],
    'saturnmoons_locs.ssc': [
        'Epimetheus', 'Janus', 'Mimas', 'Enceladus', 'Tethys', 'Dione', 'Rhea', 'Titan', 'Hyperion', 'Iapetus', 'Phoebe'
    ],
    'uranusmoons_locs.ssc': ['Puck', 'Miranda', 'Ariel', 'Umbriel', 'Titania', 'Oberon'],
    'neptunemoons_locs.ssc': ['Proteus', 'Triton'],
    'dwarfplanets_locs.ssc': ['Ceres', 'Pluto', 'Charon'],
    'asteroids_locs.ssc': [
        'Vesta', 'Lutetia', 'Eros', 'Ida', 'Dactyl', 'Mathilde', 'Gaspra', 'Steins', 'Itokawa', 'Dimorphos', 'Bennu', 'Ryugu'
    ]
}

objects = tuple(sorted(sum(sets.values(), [])))

retrograde_rotators = (
    'Ariel', 'Bennu', 'Dimorphos', 'Ida', 'Itokawa', 'Miranda', 'Oberon', 'Puck', 'Ryugu', 'Steins', 'Titania', 'Triton', 'Umbriel', 'Venus'
)

#columns = (
#   'Feature ID', 'Feature Name', 'Clean Feature Name', 'Target', 'Diameter', 'Center Latitude', 'Center Longitude',
#   'Northernmost Latitude', 'Southernmost Latitude', 'Easternmost Longitude', 'Westernmost Longitude', 'Coordinate System',
#   'Continent Ethnicity', 'Feature Type', 'Feature Type Code', 'Quad', 'Approval Status', 'Approval Date', 'Reference',
#   'Origin', 'Additional Info', 'Last Updated'
#)

celestia16supports = (
    'AA', 'AS', 'CA', 'CH', 'CM', 'CR', 'DO', 'ER', 'FL', 'FO', 'FR', 'IN', 'LF', 'LI', 'ME', 'MN', 'MO', 'PE', 'PL', 'PM',
    'RE', 'RI', 'RT', 'RU', 'TA', 'TE', 'TH', 'UN', 'VA', 'XX'
)

none_list = ('', None, 'None')
yes_list = ('y', 't', '1')
no_list = ('n', 'f', '0')


# SSC writer

def rround(num):
    if int(num) == num:
        return int(num)
    else:
        return round(num, 7)

def reader(request):
    global zero_size_counter
    locations = []
    for line in database:
        data = dict(zip(columns, line))
        target = data['Target']
        name = data['Feature Name']
        if request == target and data['Approval Status'] == 'Approved':
            location = '\n'

            # Comments
            if comments:
                if data['Approval Date'] not in none_list and data['Last Updated'] not in none_list:
                    location += f'# Approval date: {data["Approval Date"]}; Last update: {data["Last Updated"]}\n'
                if data['Origin'] not in none_list:
                    location += f'# Origin: {data["Origin"]}\n'
                if data['Additional Info'] not in none_list:
                    location += f'# Additional info: {data["Additional Info"]}\n'
            
            # Name
            if data['Feature Type Code'] in ('AL', 'ME', 'OC', 'RE', 'TA'):
                location += f'Location "{name.upper()}"'
            else:
                location += f'Location "{name}"'
            
            # Target
            if target == 'Moon':
                location += f' "Sol/Earth/Moon"\n'
            elif target in sets['marsmoons_locs.ssc']:
                location += f' "Sol/Mars/{target}"\n'
            elif target in sets['jupitermoons_locs.ssc']:
                location += f' "Sol/Jupiter/{target}"\n'
            elif target in sets['saturnmoons_locs.ssc']:
                location += f' "Sol/Saturn/{target}"\n'
            elif target in sets['uranusmoons_locs.ssc']:
                location += f' "Sol/Uranus/{target}"\n'
            elif target in sets['neptunemoons_locs.ssc']:
                location += f' "Sol/Neptune/{target}"\n'
            elif target in ('Pluto', 'Charon') and styleCO: # CO uses barycenter
                location += f' "Sol/Pluto-Charon/{target}"\n'
            elif target == 'Charon':
                location += f' "Sol/Pluto/Charon"\n'
            elif target == 'Dactyl':
                location += f' "Sol/Ida/Dactyl"\n'
            else:
                location += f' "Sol/{target}"\n'
            
            # LongLat
            location += '{\n'
            if name in custom_longlat:
                location += f'\tLongLat\t[ {custom_longlat[name]} ]\n'
            else:
                long = float(data['Center Longitude'])
                lat = float(data['Center Latitude'])
                lat_system, long_direction, long_scope = data['Coordinate System'].split(', ')
                invert_long = False
                if long_scope == '0 - 360':
                    if target == 'Vesta': # coordinate system by the Dawn team, see ReadMe
                        long -= 150
                    if long > 180:
                        long -= 360
                if long_direction == '+West':
                    invert_long = not invert_long
                if target in retrograde_rotators:
                    invert_long = not invert_long
                    lat *= -1
                if invert_long:
                    long *= -1
                location += f'\tLongLat\t[ {rround(long)} {rround(lat)} 0 ]\n'
            
            # Size/Importance
            diameter = float(data['Diameter'])
            if diameter == 0:
                zero_size_counter += 1
                if data['Feature Type Code'] == 'AL':
                    location += f'\tImportance\t20\n'
                elif name in custom_size:
                    location += f'\tSize\t{custom_size[name]}\n'
                else:
                    location += f'\tSize\t10\n'
            else:
                location += f'\tSize\t{rround(diameter)}\n'
            
            # Type
            if celestia16 and data['Feature Type Code'] not in celestia16supports:
                location += f'\tType\t"XX"'
            else:
                location += f'\tType\t"{data["Feature Type Code"]}"'
            if comments:
                location += f'\t# {data["Feature Type"]}'
            
            location += '\n}\n'
            locations.append(location)
        
    return locations

def writer(target_list, path):
    with open(path, 'w', encoding='UTF-8') as ssc:
        if len(target_list) == 1:
            target = target_list[0]
            locations = reader(target)
            print(f'{target} was processed')
            counter = f'# {len(locations)} location{"" if len(locations) == 1 else "s"} on {"the " if target == "Moon" else ""}{target}.\n'
            crutch = '\n'
        else:
            locations = []
            n = 0
            for target in target_list:
                locs = reader(target)
                n += len(locs)
                locations.append(f'\n\n# {len(locs)} location{"" if len(locs) == 1 else "s"} on {"the " if target == "Moon" else ""}{target}.\n')
                locations.append(''.join(locs))
                print(f'{target} was processed')
            target_list_temp = target_list[:-2]
            target_list_temp.append(f'{target_list[-2]} and {target_list[-1]}')
            counter = f'# {n} locations on {", ".join(target_list_temp)}.\n'
            crutch = ''
        ssc.write(counter)
        ssc.write('\n' if styleCO else '')
        ssc.write(f'# SSC-file author: CLM tool by Askaniy (https://github.com/Askaniy/CelestiaLocationsMaker)\n')
        if styleCO:
            ssc.write(f'\n# Date of creation: {today}\n')
            ssc.write(f'# Last update: {today}\n')
        ssc.write(crutch + ''.join(locations))


# Paths detection

def folder(follow_symlinks=True): # Automatic (by jfs)
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(folder)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname('/'.join(path.split('\\')))

try:
    path = folder()
except Exception:
    print('Automatic folder detection failed.')
    path = input('\nPlease enter the folder where "clm.py" is located: ')

data_path = path + '/data'
if not os.path.isfile(data_path + '/searchresults.csv'):
    print('\n"searchresults.csv" not found, please try again.\n')
    sys.exit(1)

save_path = path + '/locations'
try:
    if not os.path.exists(save_path):
        os.mkdir(save_path)
except Exception:
    print('\nCan’t find or create "locations" folder, you can try to create it manually.\n')
    sys.exit(1)



print('\n                     Welcome to Celestia Locations Maker!')


# Setting flags

# by default
celestia16 = False
styleCO = False
comments = False

if input('(1/3) Do you want to constrain location types according to Celestia 1.6? [y/n] (n): ').strip().lower() in yes_list:
    celestia16 = True
if input('(2/3) Do you want to use Celestia Origin style? [y/n] (n): ').strip().lower() in yes_list:
    styleCO = True
    comments = True
    print('(3/3) Comments about each location are on')
elif input('(3/3) Do you want to add comments to SSC about each location? [y/n] (n): ').strip().lower() in yes_list:
    comments = True


# Target selection

print('\n[1] Create SSC for each object   >[3] Create SSCs according to standard object sets')
print('[2] Select object...              [4] Select set...')

choice = input('\nPlease choose processing mode: ')

if choice == '1':
    set_list = objects

elif choice == '2':
    table = '\n'
    worklist = objects
    col_len = ceil(len(worklist) / 3)
    columns = [worklist[0:col_len], worklist[col_len:2*col_len], worklist[2*col_len:]]
    for i in range(col_len):
        table += f'[{i+1          }] {columns[0][i]}'.ljust(20)
        table += f'[{i+1 + col_len}] {columns[1][i]}'.ljust(20)
        table += f'[{i+1+2*col_len}] {columns[2][i]}\n' if i < len(columns[2]) else '\n'
    print(table)
    
    try:
        set_list = [worklist[int(input('Please enter the target number: ')) - 1]]
    except Exception:
        print('Input was wrong, please try again.\n')
        sys.exit(2)

elif choice == '3' or choice in none_list: # default one
    set_list = list(sets.items())

elif choice == '4':
    table = '\n'
    worklist = list(sets.keys())
    col_len = ceil(len(worklist) / 2)
    columns = [worklist[0:col_len], worklist[col_len:]]
    for i in range(col_len):
        table += f'[{i+1        }] {columns[0][i]}'.ljust(30)
        table += f'[{i+1+col_len}] {columns[1][i]}\n' if i < len(columns[1]) else '\n'
    print(table)
    
    try:
        set_list = [list(sets.items())[int(input('Please enter the target number: ')) - 1]]
    except Exception:
        print('Input was wrong, please try again.\n')
        sys.exit(2)

else:
    print('Input was wrong, please try again.\n')
    sys.exit(2)


# Custom coordinates and altitudes

custom_longlat = {}
try:
    with open(data_path + '/custom_longlat.txt', 'r', encoding='UTF-8') as coords:
        for line in coords:
            try:
                name, coord = line.split('\t')
                custom_longlat.update({name: coord[:-1]})
            except Exception:
                pass
except Exception:
    pass


# Sizes of zero-sized locations

custom_size = {}
try:
    with open(data_path + '/custom_size.txt', 'r', encoding='UTF-8') as zeros:
        for line in zeros:
            try:
                name, size = line.split('\t')
                custom_size.update({name: size[:-1]})
            except Exception:
                pass
except Exception:
    pass


# Database reader and export

zero_size_counter = 0
with open(data_path + '/searchresults.csv', 'r', encoding='UTF-8') as SearchResults:
    content = list(csv.reader(SearchResults))
    columns = content[0]
    database = content[1:]

    # Output file creation
    print('')
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
    #print('Zero sized locations: ', zero_size_counter)