''' File for running network calculations for CMS '''
import argparse
import time
import pandas as pd
import numpy as np

from utils.cms_rbt_parser import build_dataframe
from utils.network_helper_utils import createGraphObject
from utils.read_write_helper_utils import grab_files_onefolder, save, network_add_names

def create_dataframe(files, log):
    '''
    This function calls the Correspondence_XML_parser.py 
    file and creates our pandas dataframe.
    '''
    df = build_dataframe(files)
    print("Number of Entries: "  + str(len(df)))
    print("Average Length of Entry: " + str(df['text'].apply(len).mean()))
    log['num_entries'] = str(len(df))
    log['avg_entry_len'] = str(df['text'].apply(len).mean())

    # Lowercase values in source, target, and reference columns.
    df['source'] = df['source'].str.lower()
    df['target'] = df['target'].str.lower()
    df['references'] = df['references'].str.lower()

    # Split references into list objects.
    df['references'] = df['references'].str.split(r',|;')
    print("Average Num of People Mentioned per Entry " + str(df['references'].apply(len).mean()))
    log['pers_ref_avg'] = str(df['references'].apply(len).mean())

    return df

def create_adj_matrix(df, weight):
    ''' Creates the adjacency matrix from the dataframe '''
    # Explode list so that each list value becomes a row.
    refs = df.explode('references')
    refs['source'] = refs['source'].str.strip()
    refs['target'] = refs['target'].str.strip()
    refs['references'] = refs['references'].str.strip()

    # Create file-person matrix.
    refs = pd.crosstab(refs['file'], refs['references'])

    # Repeat with correspondence (source + target)
    source = pd.crosstab(df['file'], df['source'])
    target = pd.crosstab(df['file'], df['target'])

    # Sum values of sources to refs or create new column with sources' values.
    for col in source:
        if col in refs:
            refs[str(col)] = refs[str(col)] + source[str(col)]
        else:
            refs[str(col)] = source[str(col)]

    # Repeat for targets.
    for col in target:
        if col in refs:
            refs[str(col)] = refs[str(col)] + target[str(col)]
        else:
            refs[str(col)] = target[str(col)]

    # Convert entry-person matrix into an adjacency matrix of persons.
    refs = refs.T.dot(refs)

    # # Change diagonal values to zero. That is, a person cannot co-occur with themself.
    np.fill_diagonal(refs.values, 0)

    # Create new 'source' column that corresponds to index (person).
    refs['source'] = refs.index

    # # Reshape dataframe to focus on source, target, and weight.
    # # Rename 'people' column name to 'target'.
    df_graph = pd.melt(refs, id_vars = ['source'], var_name = 'target', value_name = 'weight') \
        .rename(columns = {'references':'target'}) \
        .query(f'(source != target) & (weight > {weight})') \
        .query('(source != "u") & (target != "u")')

    # Remove rows with empty source or target.
    df_graph['source'].replace('', np.nan, inplace=True)
    df_graph['target'].replace('', np.nan, inplace=True)
    df_graph.dropna(subset=['source', 'target'], inplace=True)

    return df_graph

def network_transform(args):
    ''' Function to run network transform '''
    log = {}
    log['weight_min'] = str(int(args.weight) + 1)
    print('Grabbing files')
    files = grab_files_onefolder(args.folder)
    print('Creating Dataframe')
    df = create_dataframe(files, log)
    print('Creating Adjacency Matrix')
    df_graph = create_adj_matrix(df, args.weight)
    print('Creating Graph Object')
    start_time = time.time()
    data = createGraphObject(df_graph, log)
    print("Creating Graph Object time:", time.time() - start_time, "seconds.")
    print('Adding Names from MHS PSC API')
    network_add_names(data)
    print('Saving data as json')
    metric = {}
    metric['metrics'] = log
    save(data, metric, args.filename)

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
        'filename',
        help='The output json filename')
    parser.add_argument(
        'weight',
        help='Weight of filter for edges')
    args = parser.parse_args()
    network_transform(args)

if __name__ == "__main__":
    main()