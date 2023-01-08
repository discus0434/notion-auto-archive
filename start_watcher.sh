export WORKSPACE_DIR=/home/workspace

cd "${WORKSPACE_DIR}/notion-auto-archive"

source venv/bin/activate
CUDA_VISIBLE_DEVICES=1 python direct_message_watcher.py
