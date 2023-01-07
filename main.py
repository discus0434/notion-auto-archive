import argparse
import logging
from logging import getLogger

from config import (
    CANDIDATE_LABELS,
    DATABASE_ID,
    JAVASCRIPT_PATH,
    JSON_PATH,
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
        javascript_path=JAVASCRIPT_PATH,
        json_path=JSON_PATH,
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


if __name__ == "__main__":
    main()
