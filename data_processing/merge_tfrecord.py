#!/usr/bin/python
import glob
# imports
import sys

import tensorflow as tf


def comb_tfrecord(tfrecords_path, save_path, batch_size=128):
    with tf.Graph().as_default(), tf.Session() as sess:
        ds = tf.data.TFRecordDataset(tfrecords_path).batch(batch_size)
        batch = ds.make_one_shot_iterator().get_next()
        writer = tf.python_io.TFRecordWriter(save_path)
        while True:
            try:
                records = sess.run(batch)
                for record in records:
                    writer.write(record)
            except tf.errors.OutOfRangeError:
                break
            except Exception as ex:
                print "unexpected ex ", ex


# main. accepts three command-line arguments: input file, output file, and the number of entries in evo profiles
if __name__ == '__main__':
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    list = glob.glob(input_path + "/*.tfrecord")

    comb_tfrecord(list, output_path)
