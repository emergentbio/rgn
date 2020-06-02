import glob
import os

import tensorflow as tf


def comb_tfrecord(tfrecords_path, save_path, batch_size=128):
    with tf.Graph().as_default(), tf.Session() as sess:
        ds = tf.data.TFRecordDataset(tfrecords_path).batch(batch_size)
        batch = ds.make_one_shot_iterator().get_next()
        writer = tf.python_io.TFRecordWriter(save_path)

        k = 0

        while True:
            try:
                records = sess.run(batch)
                for record in records:
                    writer.write(record)

                    k += 1
                    if k % 128 == 0:
                        print (k, "/", len(tfrecords_path))

            except tf.errors.OutOfRangeError:
                print "OutOfRangeError"
                break
            except Exception as ex:
                print "unexpected ex ", ex


# main. accepts three command-line arguments: input file, output file, and the number of entries in evo profiles
if __name__ == '__main__':
    # input_path = sys.argv[1]
    # output_path = sys.argv[2]

    input_path = "/d/rgn_processing2/fasta_files/"
    output_path = "/home/dev/RGN7/data/ProteinNet7Thinning90/testing/1"
    print "getting tfrecords from", input_path
    list = glob.glob(input_path + "/*.tfrecord")

    print "getting exising npy from", input_path
    existing = glob.glob(input_path + "/*.npy")

    print "getting generated npy from /home/dev/RGN7/runs/CASP7/ProteinNet7Thinning90/5/outputsTesting"
    existing2 = glob.glob("/home/dev/RGN7/runs/CASP7/ProteinNet7Thinning90/5/outputsTesting/*.npy")
    existing.extend(existing2)

    for i in range(len(existing)):
        # we take fhe file name, which is: 'A0A023IPD5 <unknown description>.npy'
        # and we stop at space
        if "unknown" in existing[i]:
            existing[i] = os.path.basename(existing[i]).split(' ')[0]
        else:
            existing[i] = os.path.basename(existing[i]).split('.')[0]
    existing_npy = set(existing)

    list_to_process = []
    n = 20000
    for i in range(len(list)):
        f = list[i]
        f_protein = os.path.basename(f).split('.')[0]

        if f_protein in existing_npy:
            # print f, "existing"
            continue

        list_to_process.append(f)

        n -= 1
        if n <= 0:
            print "stopping on i", i, "len(list)", len(list)
            break

    print "starting merging ", len(list_to_process), " tfrecords"
    print "first", list_to_process[0]
    print "last", list_to_process[len(list_to_process) - 1]
    comb_tfrecord(list_to_process, output_path)
