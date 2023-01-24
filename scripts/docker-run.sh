PROJECT_DIR="$HOME/notion-auto-archive"
mkdir -p "$PROJECT_DIR/output"


docker run -it \
    --runtime=nvidia \
    --gpus all \
    --env-file ./.env  \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $PROJECT_DIR/output:/home/workspace/notion-auto-archive/output \
    -d \
    --restart=always \
    notion-auto-archive:latest /bin/bash

docker run -it \
    --name pdf-reader \
    --runtime=nvidia \
    --gpus all \
    -v $PROJECT_DIR/pdf-reader:/home/workspace/pdf-reader \
    -v $PROJECT_DIR/output:/home/workspace/pdf-reader/output \
    -d \
    --restart=always \
    pdf-reader:latest /bin/bash

