export WORKSPACE_DIR=/home/workspace

cd $WORKSPACE_DIR/notion-auto-archive

source venv/bin/activate
python direct_message_watcher.py
