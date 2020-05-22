* Docker compose spins up the docker image with GPU, docker command line would be derived from :
    <pre>
    docker run --gpus all nvcr.io/nvidia/tensorflow:18.12-py2 nvidia-smi
    
    docker run -t -i --gpus all -p 0.0.0.0:2222:22 tensorflow:18.12-py2-setroctile
    </pre>
    using the tagged image created from Dockerfile.

* For docker compose to work, it needs a change in /etc/docker/daemon.json, specifically the path file:
    <pre>
    {
        "runtimes": {
            "nvidia": {
                "path": "/usr/bin/nvidia-container-runtime",
                "runtimeArgs": []
            }
        }
    }
    </pre>
    