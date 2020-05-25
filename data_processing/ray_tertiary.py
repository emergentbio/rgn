import glob
import multiprocessing
import os


def process_file(f, k, nfiles):
    log = ""
    if not os.path.exists(f + ".cinfo") or not os.path.exists(f + ".icinfo"):
        log += f + " skip" + "\n"
        return log

    if os.path.exists(f + ".tfrecord.npy"):
        log += f + " npy exists" + "\n"
        return log

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

    fasta_files = glob.glob("/d/rgn_processing/fasta_files/*.fasta")
    print(f"fasta files {len(fasta_files)}")

    pre_process = True

    if pre_process:
        all_files = set(glob.glob("/d/rgn_processing/fasta_files/*.fasta*"))
        print(f"all files {len(all_files)}")

        files = []
        for k, f in enumerate(fasta_files):
            if k % 1000 == 0:
                print(f"{k} / {len(fasta_files)}, files {len(files)}")

            if (f + ".tfrecord") in all_files:
                continue

            files.append(f)
    else:
        files = fasta_files

    sequential = False
    ray = True

    if sequential:
        for k in range(len(files)):
            f = files[k]
            process_file(f, k, len(files))

    if ray:
        import ray

        @ray.remote(num_cpus=1)
        def ray_process_files(f, k, nfiles):
            return process_file(f, k, nfiles)

        ray.init(address='10.2.0.4:10000', redis_password='emergent')

        ids = []
        for k in range(len(files)):
            f = files[k]
            ids.append(ray_process_files.remote(f, k, len(files)))

        while True:
            ready, not_ready = ray.wait(ids)
            print(f'Not ready {len(not_ready)}, ready: {len(ready)}')
            for r in ready:
                print(ray.get(r))

            ids = not_ready
            if not ids:
                break


if __name__ == '__main__':
    main()
