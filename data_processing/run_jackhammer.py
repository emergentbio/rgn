import os
import glob
from joblib import Parallel, delayed
import multiprocessing


def process_file(f, k, nfiles):
    if os.path.exists(f + ".cinfo") and os.path.exists(f + ".icinfo"):
        print f + " skip"
        return

    print f + " " + str(k) + " / " + str(nfiles)

    os.system("bash jackhmmer.sh " + f + " ~/d/sequence_database/proteinnet7")


def main():
    print multiprocessing.cpu_count()

    files = glob.glob("/d/rgn_processing/fasta_files/*.fasta")

    if False:
        for k in range(len(files)):
            f = files[k]
            process_file(f, k)
    else:
        Parallel(n_jobs=multiprocessing.cpu_count() / 4)(delayed(process_file)(files[k], k, len(files)) for k in range(len(files)))


if __name__ == '__main__':
    main()
