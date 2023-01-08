import argparse
import logging
import os
from logging import getLogger
from pathlib import Path

from config import (
    ARXIV_CATEGORIES,
    CACHE_PATH,
    CANDIDATE_LABELS,
    DATABASE_ID,
    GYAZO_ACCESS_TOKEN,
    NOTION_ACCESS_TOKEN,
)
from lib import get_web_content, label_text, post_to_notion


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = getLogger(__name__)
    logger.debug("Starting main function...")

    argparser = argparse.ArgumentParser()
    argparser.add_argument("url", help="URL to upload", type=str)
    args = argparser.parse_args()

    logger.debug(f"Fetching content from: {args.url}")

    processed_content = get_web_content(
        url=args.url,
        cache_path=CACHE_PATH,
        arxiv_categories=ARXIV_CATEGORIES,
    )

    logger.debug(f"Fetching content: Done!")
    logger.debug("Labeling content using mDeBERTa-v3...")

    if processed_content.tags is None:
        tags = label_text(
            text=processed_content.cleansed_content,
            candidate_labels=CANDIDATE_LABELS + list(ARXIV_CATEGORIES.values()),
            threshold=0.45,
        )
        processed_content.tags = tags

    logger.debug("Labeling content using mDeBERTa-v3: Done!")
    logger.debug("Uploading content to Notion...")

    post_to_notion(
        notion_access_token=NOTION_ACCESS_TOKEN,
        gyazo_access_token=GYAZO_ACCESS_TOKEN,
        database_id=DATABASE_ID,
        processed_content=processed_content,
        url=processed_content.url,
    )

    logger.debug("Main function: Done!")

    # remove all cache and directories without log and directories
    for root, dirs, files in os.walk(CACHE_PATH):
        for file in files:
            path = Path(os.path.join(root, file))
            if not path.name.endswith(".log"):
                os.remove(path)
    for root, dirs, files in os.walk(CACHE_PATH):
        for dir in dirs:
            path = Path(os.path.join(root, dir))
            os.rmdir(path)


if __name__ == "__main__":
    main()
