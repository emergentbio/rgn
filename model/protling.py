#!/usr/bin/python

# imports
import os
import sys
import signal
import argparse
import fileinput
import numpy as np
import tensorflow as tf
from utils import *
from os import path
from copy import deepcopy
from glob import glob
from shutil import rmtree
from pprint import pprint
from setproctitle import setproctitle
from model import RGNModel
from config import RGNConfig, RunConfig

# constant directory and file names
LOGS_DIRNAME = "logs"


def predict_tertiary(configs, models, session):
    # assumes that the validation reference designation (wt vs. unwt) can be used for the training and test sets as well
    val_ref_set_prefix = (
        "un"
        if configs["run"].optimization["validation_reference"] == "unweighted"
        else ""
    )

    for label, model in models.iteritems():
        if "eval" in label:
            dicts = model.predict(session)
            for idx, dict_ in dicts.iteritems():
                return idx, dict_["tertiary"]


def predict(args):
    # create config and model collection objects, and retrieve the run config
    configs = {}
    models = {}
    configs.update({"run": RunConfig(args.config_file)})

    # set GPU-related environmental options and config settings
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu) if args.gpu is not None else ""
    setproctitle(
        "RGN "
        + configs["run"].names["run"]
        + " on "
        + os.getenv("CUDA_VISIBLE_DEVICES", "CPU")
    )

    # derived files and directories
    checkpoints_dir = args.checkpoint

    logs_dir = os.path.join(LOGS_DIRNAME, "")


    # this is all for evaluation models (including training, so training_batch_size is for evaluation)
    full_training_glob = args.input_file
    training_invocations = configs["run"].evaluation["num_training_invocations"]

    testing_glob = args.input_file
    testing_batch_size = configs["run"].evaluation["num_testing_samples"]
    testing_invocations = configs["run"].evaluation["num_testing_invocations"]

    eval_num_epochs = 1
    training_batch_size = validation_batch_size = testing_batch_size = 1
    training_invocations = validation_invocations = testing_invocations = 1

    # select device placement taking into consideration the interaction between training and evaluation models
    if (
        configs["run"].computing["training_device"] == "GPU"
        and configs["run"].computing["evaluation_device"] == "GPU"
    ):
        fod_training = {"/cpu:0": ["point_to_coordinate"]}
        fod_evaluation = {"/cpu:0": ["point_to_coordinate"]}
        dd_training = ""
        dd_evaluation = ""
    elif (
        configs["run"].computing["training_device"] == "GPU"
        and configs["run"].computing["evaluation_device"] == "CPU"
    ):
        fod_training = {"/cpu:0": ["point_to_coordinate", "loss_history"]}
        fod_evaluation = {}
        dd_training = ""
        dd_evaluation = "/cpu:0"
    else:
        fod_training = {}
        fod_evaluation = {}
        dd_training = "/cpu:0"
        dd_evaluation = "/cpu:0"

    # create models configuration templates
    configs.update(
        {
            "training": RGNConfig(
                args.config_file,
                {
                    "name": "training",
                    "dataFilesGlob": full_training_glob,
                    "checkpointsDirectory": checkpoints_dir,
                    "logsDirectory": logs_dir,
                    "fileQueueCapacity": configs["run"].queueing[
                        "training_file_queue_capacity"
                    ],
                    "batchQueueCapacity": configs["run"].queueing[
                        "training_batch_queue_capacity"
                    ],
                    "minAfterDequeue": configs["run"].queueing[
                        "training_min_after_dequeue"
                    ],
                    "shuffle": configs["run"].queueing["training_shuffle"],
                    "tertiaryNormalization": configs["run"].loss[
                        "training_tertiary_normalization"
                    ],
                    "batchDependentNormalization": configs["run"].loss[
                        "training_batch_dependent_normalization"
                    ],
                    # "alphabetFile": None,
                    "functionsOnDevices": fod_training,
                    "defaultDevice": dd_training,
                    "fillGPU": args.fill_gpu,
                },
            )
        }
    )

    configs.update(
        {
            "evaluation": RGNConfig(
                args.config_file,
                {
                    "fileQueueCapacity": configs["run"].queueing[
                        "evaluation_file_queue_capacity"
                    ],
                    "batchQueueCapacity": configs["run"].queueing[
                        "evaluation_batch_queue_capacity"
                    ],
                    "minAfterDequeue": configs["run"].queueing[
                        "evaluation_min_after_dequeue"
                    ],
                    "shuffle": configs["run"].queueing["evaluation_shuffle"],
                    "tertiaryNormalization": configs["run"].loss[
                        "evaluation_tertiary_normalization"
                    ],
                    "batchDependentNormalization": configs["run"].loss[
                        "evaluation_batch_dependent_normalization"
                    ],
                    # "alphabetFile": alphabet_file,
                    "functionsOnDevices": fod_evaluation,
                    "defaultDevice": dd_evaluation,
                    "numEpochs": eval_num_epochs,
                    "bucketBoundaries": None,
                },
            )
        }
    )

    # Override included evaluation models with list from command-line if specified (assumes none are included and then includes ones that are specified)
    for prefix in ["", "un"]:
        for group in ["training", "validation", "testing"]:
            configs["run"].evaluation.update(
                {"include_" + prefix + "weighted_" + group: False}
            )
    for entry in args.evaluation_model:
        configs["run"].evaluation.update({"include_" + entry: True})

    # Override other command-lind arguments
    if args.gpu_fraction:
        configs["training"].computing.update({"gpu_fraction": args.gpu_fraction})

    configs["evaluation"].loss["include"] = False

    # create training model
    models = {}
    models.update({"training": RGNModel("training", configs["training"])})
    # print('*** training configuration ***')
    # pprint(configs['training'].__dict__)

    # create weighted testing evaluation model (conditional)
    if configs["run"].evaluation["include_weighted_testing"]:
        configs.update({"eval_wt_test": deepcopy(configs["evaluation"])})
        configs["eval_wt_test"].io["name"] = "evaluation_wt_testing"
        configs["eval_wt_test"].io["data_files_glob"] = testing_glob
        configs["eval_wt_test"].optimization["batch_size"] = testing_batch_size
        configs["eval_wt_test"].queueing[
            "num_evaluation_invocations"
        ] = testing_invocations
        models.update({"eval_wt_test": RGNModel("evaluation", configs["eval_wt_test"])})
        # print('\n\n\n*** weighted testing evaluation configuration ***')
        # pprint(configs['eval_wt_test'].__dict__)

    # start head model and related prep
    session = models["training"].start(models.values())
    global_step = models["training"].current_step(session)
    current_log_step = (global_step // configs["run"].io["prediction_frequency"]) + 1

    # predict or train depending on set mode behavior
    result = {}
    try:
        while not models["training"].is_done():
            pred = predict_tertiary(configs, models, session)
            if pred is not None:
                idx, tertiary = pred
                result[idx] = tertiary
    except tf.errors.OutOfRangeError:
        pass
    except:
        print("Unexpected error: ", sys.exc_info()[0])
        raise
    finally:
        if models["training"]._is_started:
            models["training"].finish(session, save=False)

    return result

# main
if __name__ == "__main__":
    # parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run RGN model with specified parameters and configuration file."
    )
    parser.add_argument(
        "--input_file",
        help="input tfrecord file to convert",
    )

    parser.add_argument("-c", "--checkpoint", required=True, type=str, help="checkpoint folder")

    parser.add_argument(
        "--config_num",
        default=7,
        type=int,
        help="configuration file num containing specification of RGN model"
    )
    args = parser.parse_args()

    args.fill_gpu = True
    args.gpu_fraction = 0.9
    args.prediction_only = True
    args.evaluation_model = ["weighted_testing"]
    args.config_file = path.join(path.dirname(__file__), ("../configurations/CASP%d.config" % args.config_num))
    args.gpu = "0"


    result = predict(args)
    print(result)
