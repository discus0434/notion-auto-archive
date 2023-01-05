import argparse
from logging import getLogger

from config import (
    CANDIDATE_LABELS,
    DATABASE_ID,
    JAVASCRIPT_PATH,
    JSON_PATH,
    NOTION_ACCESS_TOKEN,
)
from lib import get_web_content, label_text, markdown_to_notion, post_to_notion


def main():

    logger = getLogger(__name__)
    logger.debug("Starting main function...")

    argparser = argparse.ArgumentParser()
    argparser.add_argument("url", help="URL to upload", type=str)
    args = argparser.parse_args()

    logger.debug(f"Fetching content from: {args.url}")

    processed_responses = get_web_content(args.url)

    logger.debug(f"Fetching content: Done!")
    logger.debug("Converting content to Notion format...")

    notioned_content = markdown_to_notion(
        javascript_path=JAVASCRIPT_PATH,
        json_path=JSON_PATH,
        markdown_content=processed_responses.markdown_content,
    )

    logger.debug("Converting content to Notion format: Done!")
    logger.debug("Labeling content using mDeBERTa-v3...")

    tags = label_text(processed_responses.cleansed_content, CANDIDATE_LABELS, 0.45)

    logger.debug("Labeling content using mDeBERTa-v3: Done!")
    logger.debug("Uploading content to Notion...")

    post_to_notion(
        access_token=NOTION_ACCESS_TOKEN,
        database_id=DATABASE_ID,
        processed_content=processed_responses,
        tags=tags,
        url=args.url,
        notioned_content=notioned_content,
    )

    logger.debug("Main function: Done!")


if __name__ == "__main__":
    main()
