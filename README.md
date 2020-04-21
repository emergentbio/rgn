# Recurrent Geometric Networks
This is the reference (TensorFlow) implementation of recurrent geometric networks (RGNs), described in the paper [End-to-end differentiable learning of protein structure](https://www.cell.com/cell-systems/fulltext/S2405-4712(19)30076-6).

## Installation and requirements
Extract all files in the [model](https://github.com/aqlaboratory/rgn/tree/master/model) directory in a single location and use `protling.py`, described further below, to train new models and predict structures. Below are the language requirements and package dependencies:

* Python 2.7
* TensorFlow >= 1.4 (tested up to 1.12)
* setproctitle

## Usage
The [`protling.py`](https://github.com/aqlaboratory/rgn/blob/master/model/protling.py) script facilities training of and prediction using RGN models. Below are typical use cases. The script also accepts a number of command-line options whose functionality can be queried using the `--help` option.

```
python --checkpoint ./checkpoints_dir --input_file tfrecord_file [--config_num 7] 
```
