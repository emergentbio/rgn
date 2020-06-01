import glob
import os
import shutil

if __name__ == '__main__':

    input_path = "/d/rgn_processing/fasta_files/"
    list = glob.glob(input_path + "/*.fasta")

    list_short = []
    for i in range(len(list)):
        list_short.append(os.path.basename(list[i]).split('.')[0])

    list_short_set = set(list_short)

    existing = glob.glob(input_path + "/*.npy")
    existing_short = []
    for i in range(len(existing)):
        # we take fhe file name, which is: 'A0A023IPD5 <unknown description>.npy'
        # and we stop at space
        if "unknown" in existing[i]:
            existing_short.append(os.path.basename(existing[i]).split(' ')[0])
        else:
            existing_short.append(os.path.basename(existing[i]).split('.')[0])
    existing_short_set = set(existing_short)

    npy_dif_list = existing_short_set.difference(list_short_set)
    list_dif_npy = list_short_set.difference(existing_short_set)

    print(len(list_dif_npy) / len(list))

    list_missing = [f for f in list if os.path.basename(f).split('.')[0] in list_dif_npy]

    list_existing2 = glob.glob(input_path.replace("rgn_processing", "rgn_processing2") + "/*.fasta")
    list_existing2_set = set(list_existing2)

    list_missing2 = [f for f in list_missing if f.replace("rgn_processing", "rgn_processing2") not in list_existing2_set]

    for i, f in enumerate(list_missing2):
        if i % 100 == 0:
            print(i)

        target = f.replace("rgn_processing", "rgn_processing2")
        shutil.copyfile(f, target)
