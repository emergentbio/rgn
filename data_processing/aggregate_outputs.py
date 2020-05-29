import os
import numpy as np
import pandas as pd
import argparse


def aggregate_outputs(files_path, out_path):
    """
    Collect RGN outputs in one parquet file

    Args:
        files_path: path where the RGN output files exist as .npy files
        out_path: path and filename for the output file, should end with gzip to signal compression

    Returns:
        None
    """
    # get list of output files
    files = [f for f in os.listdir(files_path) if '.npy' in f]
    # initialize dataframe
    df = pd.DataFrame([], columns=['uniprot_id', 'coordinates'])
    # for each file
    num_files = len(files)
    print(f"{num_files} files to process")
    for i, file in enumerate(files):
        # get uniprot id
        if '<unknown description>' in file:
            uniprot_id = file.split(' ')[0]
        else:
            uniprot_id = file.split('.')[0]
        try:
            # load tertiary coordinates
            coords = np.load(os.path.join(files_path, file))
            # permute, flatten, convert to list
            coords = coords.T.flatten().tolist()
            # add to dataframe
            df = df.append({'uniprot_id': uniprot_id, 'coordinates': coords}, ignore_index=True)
            print(f'Completed: {i}/{num_files}', end='\r')
        except Exception as e:
            print(f"Issue loading {file}, Error: {e}")
    # save dataframe as parquet file
    df.to_parquet(out_path, compression='snappy')


if __name__ == "__main__":

    # parse command-line arguments
    parser = argparse.ArgumentParser(description="Aggregate RGN outputs into a parquet file.")
    parser.add_argument("-i", "--input_path", default='./', help="path to rgn output files to aggregate",)
    parser.add_argument("-o", "--output_path", default='./rgn_output.parquet', help="output path for parquet file")
    args = parser.parse_args()
    # run script
    aggregate_outputs(args.input_path, args.output_path)