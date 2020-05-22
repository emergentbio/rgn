* Docker compose spins up the docker image with GPU, docker command line would be derived from :
    <pre>docker run --gpus all nvcr.io/nvidia/tensorflow:18.12-py2 nvidia-smi</pre>
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
    