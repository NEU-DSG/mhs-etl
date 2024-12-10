''' File for computing subject headings '''
import argparse
import pandas as pd
import numpy as np

from etl.utils.jqa_xml_parser import build_dataframe
from etl.utils.cms_rbt_parser import build_dataframe as correspondence_build_dataframe
from etl.utils.read_write_helper_utils import grab_files_onefolder, save

def create_dataframe(files, jqa):
    ''' Script to build dataframe '''
    if jqa:
        df = build_dataframe(files)
    else:
        df = correspondence_build_dataframe(files)
    # df.to_csv("intermediate.csv")

    # Unnest subject headings. 
    df['subjects'] = df['subjects'].str.split('|')
    df = df.explode('subjects')

    # Remove leading and trailing whitespace.
    df['subjects'] = df['subjects'].str.strip()

    # Remove rows with subject of "The".
    df = df[~df['subjects'].isin(['The'])]

    # fix dates without a day (only year and month like 1842-10) with a 1 
    df['date'] = df['date'].str.replace(r'^(\d{4}-\d{1,2})$', r'\1-1', regex=True)

    # Remove rows with empty values.
    df.replace('', np.nan, inplace = True)
    df.dropna(how='all', inplace = True)
    # df.to_csv("after_drop.csv")

    return df

def subjects_by_year(df):
    ''' Calculating the subjects aggregated '''
    df['date'] = pd.to_datetime(df['date'], format = '%Y-%m-%d', errors = 'coerce')
    df = df.dropna(subset=['date']).copy() # remove Not-a-Time values.
    # df.to_csv('coerce.csv')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # Group by year & subject to get count of subjects per year.
    subjects = df.groupby(['year', 'subjects'], as_index = False)['subjects'] \
        .size() \
        .reset_index()

    subjects = subjects.drop('index', axis=1)

    subjects.columns = ['year', 'subjects', 'count']

    # Group by year and get total number of subjects per year.
    subjects['total'] = subjects.groupby('year')['count'].transform('sum')

    # Get percentage of subject for each year.
    subjects['percentage'] = round(subjects['count'] / subjects['total'], 2) * 100

    return subjects

def subject_creation(args):
    files = grab_files_onefolder(args.folder)
    df = create_dataframe(files, False)
    subjects = subjects_by_year(df)
    # subjects.to_csv(args.csv_filename)

def main():
    '''
    Main argument to parse the args and call all of the requisite functions.
    '''
    parser = argparse.ArgumentParser(description='Create Subject Graphs')
    parser.add_argument(
        'folder',
        help='The folder of MHS XML Files')
    parser.add_argument(
        'csv_filename',
        help='The output csv filename')
    args = parser.parse_args()
    print('Grabbing files')
    subject_creation(vars(args))
    


if __name__ == "__main__":
    main()