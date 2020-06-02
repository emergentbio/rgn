import glob
import multiprocessing
import os


def process_file(f, k, nfiles):
    # if k % 10 == 0:
    #     print(f"{k} / {nfiles}")

    log = ""

    # if not os.path.exists(f + ".cinfo") or not os.path.exists(f + ".icinfo"):
    #     log += f + " skip" + "\n"
    #     return log

    # if os.path.exists(f + ".tfrecord.npy"):
    #     log += f + " npy exists" + "\n"
    #     return log

    cmd = "/home/dev/miniconda/envs/py27/bin/python /home/dev/code/rgn/data_processing/convert_to_proteinnet.py " + f
    log += cmd + "\n"
    os.system(cmd)

    if not os.path.exists(f + ".proteinnet"):
        log += "** " + f + ".proteinnet missing"
        return log

    cmd = "/home/dev/miniconda/envs/py27/bin/python /home/dev/code/rgn/data_processing/convert_to_tfrecord.py " + f + ".proteinnet " + f + ".tfrecord 42"
    log += cmd + "\n"
    os.system(cmd)

    return log

    # if os.path.exists(f + ".tfrecord"):
    #     cmd = "python ../model/protling.py --checkpoint /home/dev/RGN7/runs/CASP7/ProteinNet7Thinning90/checkpoints --input_file " + f + ".tfrecord"
    #     print(cmd)
    #     os.system(cmd)
    # else:
    #     print("missing " + f + ".tfrecord")
    #
    # print "** " + f + ".tfrecord exists " + str(os.path.exists(f + ".tfrecord.npy"))


def main():
    print(f"multiprocessing.cpu_count {multiprocessing.cpu_count()}")

    fasta_files_filter = "/d/rgn_processing2/fasta_files/*.fasta"

    fasta_files = glob.glob(fasta_files_filter)
    print(f"fasta files {len(fasta_files)}")

    pre_process = True

    if pre_process:
        all_files = set(glob.glob(fasta_files_filter + "*"))
        print(f"all files {len(all_files)}")

        files = []
        for k, f in enumerate(fasta_files):
            if k % 1000 == 0:
                print(f"{k} / {len(fasta_files)}, files {len(files)}")

            if (f + ".cinfo") not in all_files or (f + ".icinfo") not in all_files:
                continue

            if (f + ".tfrecord") in all_files:
                continue

            files.append(f)
    else:
        files = fasta_files

    files.reverse()

    sequential = False
    parallel = False
    ray = True

    if sequential:
        for k in range(len(files)):
            f = files[k]
            process_file(f, k, len(files))

    if parallel:
        from joblib import Parallel, delayed

        Parallel(n_jobs=3, backend="multiprocessing")(delayed(process_file)(files[k], k, len(files)) for k in range(len(files)))

    if ray:
        import ray

        @ray.remote(num_cpus=.5)
        def ray_process_files(f, k, nfiles):
            return process_file(f, k, nfiles)

        ray.init(address='10.2.0.8:10000', redis_password='emergent')

        ids = []

        k = 0
        batch = 500
        while k < len(files) and batch > 0:
            f = files[k]
            ids.append(ray_process_files.remote(f, k, len(files)))
            k += 1
            batch -= 1

        while True:
            ready, not_ready = ray.wait(ids)
            print(f'Not ready {len(not_ready)}, ready: {len(ready)}, k {k}, files {len(files)} remaining {len(files) - k + len(not_ready)}')
            for r in ready:
                try:
                    print(ray.get(r))
                except Exception as ex:
                    print("Exception on ray get")
                    print(ex)

            ids = not_ready

            if len(ids) < 100:
                batch = 400
                while k < len(files) and batch > 0:
                    f = files[k]
                    ids.append(ray_process_files.remote(f, k, len(files)))
                    k += 1
                    batch -= 1

            if not ids:
                break


if __name__ == '__main__':
    main()
