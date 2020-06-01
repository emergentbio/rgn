#!/bin/bash

conda activate py27

while :
do
  python data_processing/merge_tfrecord.py
  # ./run.sh

  /usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose-pycharm.yml up --exit-code-from nvidia-image --abort-on-container-exit nvidia-image

  #  cp -v -n ~/RGN7/runs/CASP7/ProteinNet7Thinning90/5/outputsTesting/*.npy /d/rgn_processing/fasta_files/ &
  # rsync -amv --size-only --chmod=a=rwx -O --no-owner --no-group --progress --include='*.npy' --exclude='*' ~/RGN7/runs/CASP7/ProteinNet7Thinning90/5/outputsTesting/ /d/rgn_processing/fasta_files/ &

  # find ~/RGN7/runs/CASP7/ProteinNet7Thinning90/5/outputsTesting/ -maxdepth 1 -name '*.npy' -exec cp -n {} /d/rgn_processing/fasta_files/ +

  # rsync -mvD --size-only --progress --include='*.npy' --include='*/' --exclude='*' ~/RGN7/runs/CASP7/ProteinNet7Thinning90/5/outputsTesting/ /d/rgn_processing/fasta_files/

  rsync -r -v  --size-only --progress --include='*.npy' --exclude='*' ~/RGN7/runs/CASP7/ProteinNet7Thinning90/5/outputsTesting/ /d/rgn_processing/fasta_files/

done