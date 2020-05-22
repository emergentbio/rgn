import os
import glob
from joblib import Parallel, delayed
import multiprocessing
import time


def process_file(f, k, nfiles):
    if not os.path.exists(f + ".cinfo") or not os.path.exists(f + ".icinfo"):
        print f + " skip"
        return

    print f + " " + str(k) + " / " + str(nfiles)

    os.system("python convert_to_proteinnet.py " + f)
    os.system("python convert_to_tfrecord.py " + f + ".proteinnet " + f + ".tfrecord 42")
    os.system("python protling.py --checkpoint /home/dev/RGN7/runs/CASP7/ProteinNet7Thinning90/checkpoints --input_file /home/john/code/emergent/rgn/3/" + f + ".tfrecord")


def main():
    print multiprocessing.cpu_count()

    while True:
        files = glob.glob("/d/rgn_processing/fasta_files/*.fasta")
        files2 = []
        for f in files:
            if os.path.exists(f + ".cinfo") and os.path.exists(f + ".icinfo"):
                files2.append(f)

        print len(files)

        if len(files) == 0:
            print "no files, sleeping 30 seconds"
            time.sleep(30)

        if False:
            for k in range(len(files)):
                f = files[k]
                process_file(f, k)
        else:
            Parallel(n_jobs=2)(delayed(process_file)(files[k], k, len(files)) for k in range(len(files)))


if __name__ == '__main__':
    main()
