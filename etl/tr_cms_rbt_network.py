''' File for running network calculations for CMS '''
import argparse
import time
import pandas as pd
import numpy as np

from etl.utils.cms_rbt_parser import build_dataframe
from etl.utils.network_helper_utils import createGraphObject
from etl.utils.read_write_helper_utils import grab_files_onefolder, save, network_add_names

def create_dataframe(files, log):
    '''
    This function calls the Correspondence_XML_parser.py 
    file and creates our pandas dataframe.
    '''
    df = build_dataframe(files)
    # df.to_csv("debug/build.csv")
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
    # df['target'] = df['target'].str.split(r',|;')
    # df.to_csv("debug/split.csv")
    print("Average Num of People Mentioned per Entry " + str(df['references'].apply(len).mean()))
    log['pers_ref_avg'] = str(df['references'].apply(len).mean())
    print("length of df after create dataframe", df.shape)

    return df

def create_adj_matrix(df, weight):
    ''' Creates the adjacency matrix from the dataframe '''
    # Explode list so that each list value becomes a row.
    refs = df.explode('references')
    print("length of df after explosion", refs.shape)
    # refs = refs.explode('target')
    refs['source'] = refs['source'].str.strip()
    refs['target'] = refs['target'].str.strip()
    refs['references'] = refs['references'].str.strip()
    # refs.to_csv("explode.csv")

    # Create file-person matrix.
    refs = pd.crosstab(refs['file'], refs['references'])
    print("length of df after crosstab", refs.shape)
    # refs.to_csv("debug/adj.csv")

    # Repeat with correspondence (source + target)
    # source = pd.crosstab(df['file'], df['source'])
    # source.to_csv("debug/source.csv")

    # print("length of source after crosstab", source.shape)
    # print(source['file'])
    '''
    We need to make a copy of the df to make a separate df_target dataframe
    for letters in which there are multiple targets/recipients. later in the 
    code we add targets to the columns of the refs, either adding the column
    value to the existing column (if the recipient was also a reference), or 
    adding the column itself otherwise. The issue here is if a target was only
    a target in a letter with multiple targets. That means that when we process 
    the pd.crosstab for the targets, there is no singular target column to add
    to the refs column.

    1/6/25 Update is that this is too complicated to handle with all of the 
    edge cases on whether there are multiple authors, multiple targets, and no 
    authors or no targets. I think it's best for the author and targets to stay
    out of the co-reference counting. There's an argument for that anyway, in the
    sense that the source and the target aren't technically being referenced within
    the entry.
    '''
    
    # df_target = df.copy(deep=True)
    # df_target['target'] = df_target['target'].str.split(r',|;')
    # df_target.to_csv("debug/df_target.csv")
    # df_target = df_target.explode('target')
    # df_target['target'] = df_target['target'].str.strip()
    
    # target = pd.crosstab(df_target['file'], df_target['target'])
    # # target = pd.crosstab(df['file'], df['target'])
    # target.to_csv("debug/target.csv")

    # Sum values of sources to refs or create new column with sources' values.
    # print("length of refs: ", len(refs))
    # print("length of source: ", len(source))
    # for col in source:
    #     if col in refs:
    #         refs[str(col)] = refs[str(col)] + source[str(col)]
    #     else:
    #         refs[str(col)] = source[str(col)]

    # Repeat for targets.
    # refs.to_csv("debug/before.csv")
    # for col in target:
    #     if ';' in col:
    #         cols = [item.strip() for item in col.split(';')]
    #         for columns in cols:
    #             if columns in refs:
    #                 refs[str(columns)] = refs[str(columns)] + target[str(columns)]
    #             else:
    #                 refs[str(columns)] = target[str(columns)]
    #     else:
    #         if col in refs:
    #             refs[str(col)] = refs[str(col)] + target[str(col)]
    #         else:
    #             refs[str(col)] = target[str(col)]

    # refs.to_csv("debug/after.csv")

    # Convert entry-person matrix into an adjacency matrix of persons.
    refs = refs.T.dot(refs)
    # refs.to_csv("debug/dot.csv")

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
    log['weight_min'] = str(int(args['weight']) + 1)
    print('Grabbing files')
    files = grab_files_onefolder(args['input'])
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
        'filename',
        help='The output json filename')
    parser.add_argument(
        'weight',
        help='Weight of filter for edges')
    args = parser.parse_args()
    network_transform(vars(args))

if __name__ == "__main__":
    main()