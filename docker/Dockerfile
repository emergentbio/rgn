FROM continuumio/anaconda3:latest

RUN apt-get update && \
    apt-get -y install gcc g++ make wget tar gzip rsync --fix-missing && \
    apt-get clean && \
    wget -c http://eddylab.org/software/hmmer/hmmer-3.3.tar.gz && \
    tar xzvf hmmer-3.3.tar.gz && \
    cd hmmer-3.3 && \
    ./configure && \
    make -j8 && \
    make install && \
    cd easel && \
    make install && \
    apt-get -y purge gcc g++ make wget && \
    useradd -ms /bin/bash dev

USER dev
WORKDIR /home/dev

RUN conda config --prepend pkgs_dirs /home/dev/pkgs_envs && \
    conda config --show envs_dirs && \
    conda config --show pkgs_dirs && \
    conda create -n py27 python=2.7.18 -y && \
    conda create -n py37 python=3.7.7 -y && \
    conda clean -afy

# envs_dirs:
#   - /home/dev/.conda/envs
#   - /opt/conda/envs

SHELL ["conda", "run", "-n", "py27", "/bin/bash", "-c"]
RUN pip --no-cache-dir install tensorflow==1.12.0

SHELL ["conda", "run", "-n", "py37", "/bin/bash", "-c"]
RUN pip --no-cache-dir install -U https://ray-wheels.s3-us-west-2.amazonaws.com/master/0f54d5ab656b55ab7e6b28f5bd61e2dd64feb0dc/ray-0.9.0.dev0-cp37-cp37m-manylinux1_x86_64.whl

#CMD [ "/bin/bash" ]
#ENTRYPOINT ["conda", "run", "-n", "py37", "python", "run.py"]
ENTRYPOINT ["conda", "run", "-n", "py37", "/bin/bash"]