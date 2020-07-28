# Running primary sequence to 3D protein structure

We are using CASP7 TF records and CASP7 model pre-trained, based on https://github.com/aqlaboratory/rgn repo.

<pre>
# run a fasta primary sequence in hmmer3
~/dev/rgn/data_processing/jackhmmer.sh {file.fasta} ~/dev/sequence_database/proteinnet7

# the output files will be generated in the same filder as {file.fasta}
# the relevant files are: .cinfo and .icinfo (extra extension at the end of {file.fasta})
# extra, unnecessary files are .tblout .a2m .sto .weighted.sto - in case of large files generation, best to clean up

# the next commands from this repo are intended for py27
cd 
conda activate py27
python ~/dev/rgn/data_processing/convert_to_proteinnet.py {file.fasta} # this uses .cinfo and .icinfo
# and creates .proteinnet

python ~/dev/rgn/data_processing/convert_to_tfrecord.py {file.fasta}.proteinnet {file.fasta}.tfrecord 42 

# the next step merges multiple tfrecord using merge_tfrecord.py

# call run.sh, that using docker-compose specifies parameters on nvidia docker image and
# just runs a command to generate teriary structure and exists

</pre>

## Prerequisites

Please ensure that you have latest docker and docker-compose, following the installations from the official website:
- https://docs.docker.com/engine/install/ubuntu/
- https://docs.docker.com/compose/install/
There are plenty of other versions, apt standard is old, snap installed versions kind of are latest as well, but the
official ones are preferred. 

On docker, install https://github.com/NVIDIA/nvidia-container-runtime, do the /etc/docker/daemon.json change or creation
and
<pre>
sudo systemctl daemon-reload
sudo systemctl restart docker
</pre>
 
Download the pretrained model:
- from https://github.com/aqlaboratory/rgn
- download: https://sharehost.hms.harvard.edu/sysbio/alquraishi/rgn_models/RGN7.tar.gz

Download the TF records for CASP7:
- https://github.com/aqlaboratory/proteinnet
- specifically, https://sharehost.hms.harvard.edu/sysbio/alquraishi/proteinnet/tfrecords/casp7.tar.gz

Raw sequences, from which the TF records have been generated are are available in (no need to download them):
- https://github.com/aqlaboratory/proteinnet/blob/master/docs/raw_data.md
- specifically https://sharehost.hms.harvard.edu/sysbio/alquraishi/proteinnet/sequence_dbs/proteinnet7.gz

This is based on docker/Dockerfile. As a script.

<pre>

mkdir ~/dev
cd ~/dev

# ensure that this repo, feature-rgn-service branch is cloned in ~/dev/rng
# such that ~/dev/rgn/data_processing/jackhmmer.sh exists
git clone https://github.com/emergentbio/rgn.git
cd rgn
git checkout feature-rgn-service
chmod +x ~/dev/rgn/data_processing/jackhmmer.sh # just in case

cd ~/dev

# Install hmmer3:
sudo apt-get update && \
    sudo apt-get -y install gcc g++ make wget tar gzip rsync --fix-missing && \
    sudo apt-get clean
    
wget -c http://eddylab.org/software/hmmer/hmmer-3.3.tar.gz && \
    tar xzvf hmmer-3.3.tar.gz && \
    cd hmmer-3.3 && \
    ./configure && \
    make -j$(nproc) && \
    sudo make install && \
    cd easel && \
    sudo make install
    
cd ~/dev

# Python 2.7 and Python 3.7

conda create -n py27 python=2.7.18 numpy -y # this is needed for for converting ProteinNet to 3d Structure
conda activate py27
pip install tensorflow==1.12.0

conda create -n py37 python=3.7.7 -y # this is needed for running ray distributed hmmer3, for single protein, manual run on hmmer3 it is not needed
conda activate py37
pip --no-cache-dir install -U https://ray-wheels.s3-us-west-2.amazonaws.com/master/0f54d5ab656b55ab7e6b28f5bd61e2dd64feb0dc/ray-0.9.0.dev0-cp37-cp37m-manylinux1_x86_64.whl

wget -c https://sharehost.hms.harvard.edu/sysbio/alquraishi/rgn_models/RGN7.tar.gz
tar xzvf RGN7.tar.gz

wget -c https://sharehost.hms.harvard.edu/sysbio/alquraishi/proteinnet/sequence_dbs/proteinnet7.gz
gzip -d proteinnet7.gz
mkdir -p ~/dev/sequence_database
mv proteinnet7 ~/dev/sequence_database/proteinnet7
</pre>