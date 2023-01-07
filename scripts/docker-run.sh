mkdir -p ./engrafo

docker run -it \
    --runtime=nvidia \
    --gpus all \
    --env-file ./.env  \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ./engrafo:/home/workspace/engrafo \
    -d \
    --restart=always \
    notion-auto-archive:latest /bin/bash

docker run -it \
    -v ./engrafo:/app/output \
    -d \
    arxivvanity/engrafo:latest /bin/bash
