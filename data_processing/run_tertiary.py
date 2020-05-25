import os
import glob
from joblib import Parallel, delayed
import multiprocessing
import time


def process_file(f, k, nfiles):
    if not os.path.exists(f + ".cinfo") or not os.path.exists(f + ".icinfo"):
        print f + " skip"
        return

    if os.path.exists(f + ".tfrecord.npy"):
        print f + " npy exists"
        return

    print f + " " + str(k) + " / " + str(nfiles)

    cmd = "python convert_to_proteinnet.py " + f
    print(cmd)
    os.system(cmd)

    if not os.path.exists(f + ".proteinnet"):
        print("** " + f + ".proteinnet missing")
        return

    cmd = "python convert_to_tfrecord.py " + f + ".proteinnet " + f + ".tfrecord 42"
    print(cmd)
    os.system(cmd)

    if os.path.exists(f + ".tfrecord"):
        cmd = "python ../model/protling.py --checkpoint /home/dev/RGN7/runs/CASP7/ProteinNet7Thinning90/checkpoints --input_file " + f + ".tfrecord"
        print(cmd)
        os.system(cmd)
    else:
        print("missing " + f + ".tfrecord")

    print "** " + f + ".tfrecord exists " + str(os.path.exists(f + ".tfrecord.npy"))


def main():
    print multiprocessing.cpu_count()

    while True:
        files = glob.glob("/d/rgn_processing/fasta_files/*.fasta")
        files2 = []
        for f in files:
            if os.path.exists(f + ".cinfo") and os.path.exists(f + ".icinfo"):
                if not os.path.exists(f + ".tfrecord.npy"):
                    files2.append(f)

                    if len(files2) > 100:
                        break

        files = files2

        files.reverse()

        print len(files)

        if len(files2) == 0:
            print "no files, sleeping 30 seconds"
            time.sleep(30)

        sequential = False

        if sequential:
            for k in range(len(files)):
                f = files[k]
                process_file(f, k, len(files))
        else:
            Parallel(n_jobs=2)(delayed(process_file)(files[k], k, len(files)) for k in range(len(files)))


if __name__ == '__main__':
    main()
