import argparse
import logging
import os
from logging import getLogger
from pathlib import Path

from config import CACHE_PATH, CANDIDATE_LABELS, DATABASE_ID, NOTION_ACCESS_TOKEN
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
    )

    logger.debug(f"Fetching content: Done!")
    logger.debug("Labeling content using mDeBERTa-v3...")

    tags = label_text(processed_content.cleansed_content, CANDIDATE_LABELS, 0.45)

    logger.debug("Labeling content using mDeBERTa-v3: Done!")
    logger.debug("Uploading content to Notion...")

    post_to_notion(
        access_token=NOTION_ACCESS_TOKEN,
        database_id=DATABASE_ID,
        processed_content=processed_content,
        tags=tags,
        url=args.url,
    )

    logger.debug("Main function: Done!")

    # remove all cache and directories without log and directories
    for root, dirs, files in os.walk(CACHE_PATH):
        for file in files:
            path = Path(os.path.join(root, file))
            if not path.name.endswith(".log"):
                os.remove(path)
        for dir in dirs:
            path = Path(os.path.join(root, dir))
            os.rmdir(path)


if __name__ == "__main__":
    main()
