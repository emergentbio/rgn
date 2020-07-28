#!/bin/bash

docker-compose -f docker-compose.yml up --exit-code-from nvidia-image --abort-on-container-exit nvidia-image
