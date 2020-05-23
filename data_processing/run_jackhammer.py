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
    print "multiprocessing.cpu_count", multiprocessing.cpu_count()

    files = glob.glob("/d/rgn_processing/fasta_files/*.fasta*")

    files2 = []
    for k in range(len(files)):
        f = files[k]
        if k % 1000 == 0:
            print str(k) + " / " + str(len(files))

        if not f.endswith(".fasta"):
            continue

        # if os.path.exists(f + ".cinfo") and os.path.exists(f + ".icinfo"):
        #     continue

        if (f + ".cinfo") in files and (f + ".icinfo") in files:
            continue

        files2.append(f)

        # if len(files2) > 200:
        #     break

    files = files2

    sequential = False

    if sequential:
        for k in range(len(files)):
            f = files[k]
            process_file(f, k, len(files))
    else:
        n_jobs = multiprocessing.cpu_count() / 4
        print "n_jobs", n_jobs

        Parallel(n_jobs=n_jobs, backend="multiprocessing")(delayed(process_file)(files[k], k, len(files)) for k in range(len(files)))


if __name__ == '__main__':
    main()
