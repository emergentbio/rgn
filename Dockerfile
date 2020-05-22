FROM nvcr.io/nvidia/tensorflow:18.12-py2
#FROM tensorflow/tensorflow:1.12.0-gpu
#FROM tensorflow/tensorflow:1.12.0-gpu-py3

WORKDIR /app
RUN pip install setproctitle
COPY ./ ./

CMD bash
