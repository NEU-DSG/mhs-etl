'''Helper file for reading and writing files'''
import os
import json
from datetime import datetime
import re
import requests
import xml.etree.ElementTree as ET

def get_tei_date(xml_file):
    """Extract the creation date from a CMS/RBT XML file."""
    try:
        root = ET.parse(xml_file).getroot()
        ns_match = re.match(r"\{(.*)}", root.tag)
        if not ns_match:
            return None
        ns = {"ns": ns_match.group(1)}
        date_elem = root.find('.//ns:date/[@type="creation"]', ns)
        if date_elem is None:
            return None
        return date_elem.get("when") or date_elem.get("notBefore")
    except ET.ParseError:
        return None
 
 
def grab_files_month_cms_rbt(folder, start_date_str, end_date_str):
    """Return XML files whose creation date falls within start–end range (YYYY or YYYY-MM)."""
    files = []
    # Accept both YYYY and YYYY-MM: YYYY expands to -01 for start, -12 for end. This is for both RBT and CMS
    start = datetime.strptime(start_date_str if "-" in start_date_str else start_date_str + "-01", "%Y-%m")
    end = datetime.strptime(end_date_str if "-" in end_date_str else end_date_str + "-12", "%Y-%m")
 
    for dirpath, _, filenames in os.walk(folder):
        for fname in sorted(f for f in filenames if f.endswith(".xml")):
            path = os.path.join(dirpath, fname)
            date_str = get_tei_date(path)
            if not date_str:
                continue
            date_str = date_str[:7] if len(date_str) >= 7 else date_str + "-01"
            date = datetime.strptime(date_str, "%Y-%m")
            if start <= date <= end:
                files.append(path)
 
    return files

def grab_files(folder, start_year, end_year):
    '''Takes in the folder for the XML docs and how many xml documents you would like to use.'''
    files = []
    # Loop through the folders and filter based on the desired range
    for dirpath, _, filenames in os.walk(folder):
        # Extract the folder name which contains the year
        folder_name = os.path.basename(dirpath)
        try:
            folder_year = int(folder_name)
        except ValueError:
            # Skip if the folder name is not a valid integer
            continue
        # Check if the folder year is within the desired range
        if start_year <= folder_year <= end_year:
            for filename in [f for f in filenames if f.endswith(".xml")]:
                files.append(os.path.join(dirpath, filename))
    # Return the specified number of files or all if length is greater than available files
    return files

def grab_files_onefolder(folder):
    '''Takes in the folder for the XML docs and how many xml documents you would like to use.'''
    files = []
    # The way this folder is laid out may change because its different than the other authors.
    for dirpath, _, filenames in os.walk(folder):
        for filename in [f for f in filenames if f.endswith(".xml")]:
            files.append(os.path.join(dirpath, filename))
    return files

def grab_files_month(folder, start_date_str, end_date_str):
    ''' 
    Takes in the folder and start and end date by 
    the month and returns the requisite JQA files
    '''
    files = []
    start_date = datetime.strptime(start_date_str, '%Y-%m')
    end_date = datetime.strptime(end_date_str, '%Y-%m')
    # regex for xml filename extraction
    pattern = r'\b(\d{4})-(\d{2})\b'
    for dirpath, _, filenames in os.walk(folder):
        for filename in [f for f in filenames if f.endswith(".xml")]:
            match = re.search(pattern, filename)
            if match:
                date = datetime.strptime(match[0], '%Y-%m')
                if start_date <= date <= end_date:
                    files.append(os.path.join(dirpath, filename))
            else:
                print(filename)
    return files

def save(data, log, filename):
    '''Simple function just to save the json file to the data folder.'''
    with open(filename, "w", encoding='utf-8') as f:
        json.dump((log | data), f, ensure_ascii=False, indent=4)

def network_add_names(data):
    '''
    This function loads the idtoname.json file, which is a dictionary 
    used to store and track the relationship between the ids and the names of the people. 
    Load the file, and check if the current nodes are tracked in the json file, and if
    not, we call the PSC names database API to fill in the names and add it to the json.
    '''
    # Open idtoname json and load it.
    with open('data/idtoname.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    # Iterate over all of the nodes
    for node in data['nodes']:
        # If the node already exists in our json, then we can just add the name to the node
        # This can be edited if we want additional information from the PSC API in the node
        if node['id'] in d:
            node['given_name'] = d[node['id']]['given_name']
            node['middle_name'] = d[node['id']]['middle_name']
            node['family_name'] = d[node['id']]['family_name']
            node['date_of_birth'] = d[node['id']]['date_of_birth']
            node['date_of_death'] = d[node['id']]['date_of_death']
        else:
            print(node['id'])
            # Otherwise, we make a requests call to the PSC
            # database API to grab the names information
            request_url = f"https://primarysourcecoop.org/mhs-api/ext/names?huscs={node['id']}"
            try:
                response = requests.get(request_url, verify=False, timeout=60)
                json_data = response.json()['data']
                if json_data:
                    node['given_name'] = json_data[node['id']]['given_name']
                    node['middle_name'] = json_data[node['id']]['middle_name']
                    node['family_name'] = json_data[node['id']]['family_name']
                    node['date_of_birth'] = json_data[node['id']]['date_of_birth']
                    node['date_of_death'] = json_data[node['id']]['date_of_death']
                    # And we add the name API response to our json for safe keeping
                    d[node['id']] = json_data[node['id']]
                # I was running into a case with sedgewick-theodoreI where there
                # was no json response. I'm not sure if this is an error or not
                # But I just set the node properties to the id and empty strings
                else:
                    node['given_name'] = node['id']
                    node['middle_name'] = ""
                    node['family_name'] = ""
                    node['date_of_birth'] = ""
                    node['date_of_death'] = ""
                    # I also add it to the dictionary so it is not called (and failed) repeatedly.
                    d[node['id']] = {
                        'given_name': node['id'],
                        'middle_name': "",
                        'family_name': "",
                        'date_of_birth': "",
                        'date_of_death': "",
                    }

            except requests.exceptions.RequestException as e:
                raise SystemExit(e) from e
    # Write out to the json
    with open('data/idtoname.json', 'w', encoding='utf-8') as f:
        json.dump(d, f)