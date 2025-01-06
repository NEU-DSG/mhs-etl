''' File for pulling XML documents from DSG PSC XML database '''
import configparser
import argparse
from datetime import datetime
import os
from lxml import etree
import requests

def pull_index(edition, credentials):
    ''' Pulls the list of XML documents from a particular edition '''
    try:
        r = requests.get(f'https://dsg.xmldb-dev.northeastern.edu/basex/rest/psc/{edition}',
                        auth=(credentials['username'],credentials['password']), timeout=10)
        r.raise_for_status()
        return r.text
    except requests.exceptions.HTTPError as http_error:
        print("HTTP error:", http_error)
        raise
    except requests.exceptions.ConnectionError as conn_error:
        print("Connection error:", conn_error)
        raise
    except requests.exceptions.Timeout as time_error:
        print("Timeout error:", time_error)
        raise
    except requests.exceptions.RequestException as error:
        print("General error:", error)
        raise

def pull_edition(edition, index, credentials, folder):
    ''' Pulls all the edition's XML documents '''
    tree = etree.fromstring(index)
    namespaces = {'ns': 'http://basex.org/rest'}
    resource_files = tree.xpath('//ns:resource/text()', namespaces=namespaces)
    for resource in resource_files:
        try:
            r = requests.get(f'https://dsg.xmldb-dev.northeastern.edu/basex/rest/psc/{edition}/{resource}',
                            auth=(credentials['username'], credentials['password']), timeout=10)
            r.raise_for_status()
            with open(folder + resource, 'w', encoding='utf-8') as f:
                f.write(r.text)
        except requests.exceptions.HTTPError as http_error:
            print("HTTP error:", http_error)
            raise
        except requests.exceptions.ConnectionError as conn_error:
            print("Connection error:", conn_error)
            raise
        except requests.exceptions.Timeout as time_error:
            print("Timeout error:", time_error)
            raise
        except requests.exceptions.RequestException as error:
            print("General error:", error)
            raise


def extract(args):
    ''' function to run extraction from dsg db '''
    config = configparser.ConfigParser()
    config.read('.config')
    credentials = dict(config.items('PSC'))
    if "all" in args['editions']:
        print("Fetching all editions...")
        for edition in ['jqa', 'cms', 'rbt', 'esr']:
            print(f"Fetching edition: {edition}")
            current_date = datetime.now().strftime("%m-%d-%y")
            folder = 'data/extract/' + edition + '-' + current_date + '/'
            os.makedirs(folder, exist_ok=True)
            index = pull_index(edition, credentials)
            pull_edition(edition, index, credentials, folder)
    else:
        print(f"Fetching edition(s): {', '.join(args['editions'])}")
        for edition in args['editions']:
            current_date = datetime.now().strftime("%m-%d-%y")
            folder = 'data/extract/' + edition + '-' + current_date + '/'
            os.makedirs(folder, exist_ok=True)
            index = pull_index(edition, credentials)
            pull_edition(edition, index, credentials, folder)

def main():
    """
    Read in PSC username and password from a local configuration file, 
    connect to PSC with and pull the relevant editions selected.
    """

    # Assumes there is a .config file with the user's PSC username and password in
    # the directory from which this script is run
    parser = argparse.ArgumentParser(description="Pull editions")
    parser.add_argument(
        "--editions",
        choices=["jqa", "cms", "rbt", "esr", "all"],
        nargs="+",  # Allows selecting multiple types
        help="Select one or more editions: JQA, CMS, RBT, ESR, or all of the editions."
    )
    args = parser.parse_args()
    extract(vars(args))

    

if __name__ == "__main__":
    main()
