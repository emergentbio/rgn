import pandas as pd
import sys
from os.path import join as path_join

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO


def seq_to_fasta(uniprot_id, protein_sequence, save_dir):
    seq = Seq(protein_sequence)
    seq_record = SeqRecord(seq, id=uniprot_id)
    SeqIO.write(seq_record, path_join(save_dir, f"{uniprot_id}.fasta"), "fasta")


if __name__ == "__main__":

    data_path = sys.argv[1]
    save_dir = sys.argv[2]

    df = pd.read_csv(data_path)

    _ = df.apply(lambda row: seq_to_fasta(row['uniprot_id'], row['sequence'], save_dir), axis=1)
