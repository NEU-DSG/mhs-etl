''' File for running network calculations for JQA '''
import argparse
import time
import pandas as pd
import numpy as np

# Import project-specific functions.

from etl.utils.jqa_xml_parser import build_dataframe
from etl.utils.network_helper_utils import createGraphObject
from etl.utils.read_write_helper_utils import grab_files_month, save, network_add_names

def create_dataframe(files, log):
    '''Builds dataframe from the files list.'''
    # Build dataframe from XML files.
    # build_dataframe() called from Correspondence_XML_parser
    df = build_dataframe(files)
    # df.to_csv("debug/build.csv")
    print("Number of Entries: ", num_entries := str(len(df)))
    log['num_entries'] = num_entries
    print("Average Length of Entry: ", avg_entry_length := str(df['text'].apply(len).mean()))
    log['avg_entry_len'] = avg_entry_length
    # Unnest people. 
    df['people'] = df['people'].str.split(r',|;')
    # df.to_csv("debug/split.csv")
    print("Average Num of People Mentioned per Entry ", \
          pers_ref_avg := str(df['people'].apply(len).mean()))
    log['pers_ref_avg'] = pers_ref_avg
    df = df.explode('people')

    # Remove leading and trailing whitespace.
    df['people'] = df['people'].str.strip()

    # Remove rows with empty values.
    df.replace('', np.nan, inplace = True)
    df.dropna(inplace = True)

    return df

def create_adj_matrix(df, weight):
    ''' Creates the adjacency matrix from the dataframe '''
    # Filter dates by unknown people
    df = df.query('(people != "u") & (people != "source")') 

    # Create adjacency matrix.
    adj = pd.crosstab(df['entry'], df['people'])
    # adj.to_csv("debug/adj.csv")

    # Convert entry-person matrix into an adjacency matrix of persons.
    adj = adj.T.dot(adj)
    # adj.to_csv("debug/dot.csv")

    # Change same-same connections to zero.
    np.fill_diagonal(adj.values, 0)

    adj['source'] = adj.index

    df_graph = pd.melt(adj, id_vars = 'source', var_name = 'target', value_name = 'weight') \
        .query(f'(source != target) & (weight >= {weight})') # this is where nodes get filtered out
    return df_graph

def network_transform(args):
    ''' Function to run transform '''
    log = {}
    log['start_month_year'] = args['start']
    log['end_month_year'] = args['end']
    log['weight_min'] = str(int(args['weight']))
    print('Grabbing files')
    files = grab_files_month(args['input'], args['start'], args['end'])  
    print('Creating Dataframe')
    df = create_dataframe(files, log)
    print('Creating Adjacency Matrix')
    df_graph = create_adj_matrix(df, args['weight'])
    print('Creating Graph Object')
    start_time = time.time()
    data = createGraphObject(df_graph, log)
    print("Creating Graph Object time:", time.time() - start_time, "seconds.")
    print('Adding Names from MHS PSC API')
    network_add_names(data)
    print('Saving data as json')
    metric = {}
    metric['metrics'] = log
    save(data, metric, args['output'])


def main():
    '''
    Main argument to parse the args and call all of the requisite functions.
    Once this runs, you can start a server and check out the index.html file.
    '''
    parser = argparse.ArgumentParser(description='Create Network Graph')
    parser.add_argument(
        'folder',
        help='The folder of MHS XML Files')
    parser.add_argument(
        'start_month_year',
        help='Start year of JQA files')
    parser.add_argument(
        'end_month_year',
        help='End year of JQA files')
    parser.add_argument(
        'filename',
        help='The output json filename')
    parser.add_argument(
        'weight',
        help='Weight of filter for edges'
    )
    args = parser.parse_args()
    network_transform(vars(args))

if __name__ == "__main__":
    main()
    