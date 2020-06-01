import glob
import multiprocessing
import os


def process_file(f, k, nfiles):
    # print(f"{f} {k} / {nfiles}")

    log = ""

    try:
        if os.path.exists(f + ".cinfo") and os.path.exists(f + ".icinfo"):
            log += f"{f}: files already exist {f}.cinfo {f}.icinfo\n"
        else:
            os.system(f"bash /home/dev/code/rgn/data_processing/jackhmmer.sh {f} /home/dev/d/sequence_database/proteinnet7")

        # cleanup
        if os.path.exists(f + ".cinfo") and os.path.exists(f + ".icinfo"):
            for extra in ["tblout", "a2m", "sto", "weighted.sto"]:
                extra_file = f + "." + extra
                if os.path.exists(extra_file):
                    try:
                        os.remove(extra_file)
                        log += f"{extra_file} removed\n"
                    except Exception as ex:
                        log += f"{extra_file} remove failure {ex}\n"

            log += f"{f}: files created: {f}.cinfo {f}.icinfo\n"
        else:
            log += f"{f}: files NOT created: {f}.cinfo {f}.icinfo\n"

    except Exception as ex:
        log += f"{f}: exception {ex}\n"

    return log


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

            # if os.path.exists(f + ".cinfo") and os.path.exists(f + ".icinfo"):
            #     continue

            if (f + ".cinfo") in all_files and (f + ".icinfo") in all_files:
                for extra in ["tblout", "a2m", "sto", "weighted.sto"]:
                    extra_file = f + "." + extra
                    if extra_file in all_files:
                        try:
                            os.remove(extra_file)
                        except Exception:
                            pass

                continue

            files.append(f)
    else:
        files = fasta_files

    print(f"final files {len(files)}")

    sequential = False
    parallel = False
    ray = True

    if sequential:
        for k in range(len(files)):
            f = files[k]
            process_file(f, k, len(files))

    if parallel:
        from joblib import Parallel, delayed

        n_jobs = multiprocessing.cpu_count() / 4
        print(f"n_jobs {n_jobs}")

        Parallel(n_jobs=n_jobs, backend="multiprocessing")(delayed(process_file)(files[k], k, len(files)) for k in range(len(files)))

    if ray:
        import ray

        @ray.remote(num_cpus=4)
        def ray_process_files(f, k, nfiles):
            return process_file(f, k, nfiles)

        ray.init(address='10.2.0.4:10000', redis_password='emergent')

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
