FROM nvcr.io/nvidia/tensorflow:18.12-py2

WORKDIR /app
RUN pip install setproctitle
COPY ./ ./

CMD
