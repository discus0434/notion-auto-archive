ARXIV_ID=$1
OUTPUT_DIR=$2

cd /home/workspace/notion-auto-archive

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
curl "https://arxiv.org/e-print/$ARXIV_ID" | tar xz

echo "Downloaded $ARXIV_ID into $OUTPUT_DIR"
