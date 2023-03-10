import sys
import time
import subprocess
import logging
from logging import getLogger

import schedule
from tweepy import Client

from config import (
    TWITTER_ACCESS_TOKEN,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_BEARER_TOKEN,
    TWITTER_TOKEN_SECRET,
    TWITTER_USER_NAME,
    URLS_LOG_PATH,
)
from lib import compare_and_save_urls, retrieve_urls_from_direct_message


def task():
    urls = retrieve_urls_from_direct_message(client, user_name=TWITTER_USER_NAME)
    new_urls = compare_and_save_urls(urls, urls_save_path=URLS_LOG_PATH)

    if new_urls:
        logger.info(f"Found new url: {new_urls}")

        for url in new_urls:
            logger.info(f"Starting to process and upload to Notion: {url}")

            try:
                subprocess.run(
                    ["python", "main.py", url],
                )
            except Exception as e:
                logger.info(f"Failed to process and upload to Notion: {url}")
                continue

            logger.info(f"Finished processing and uploading to Notion: {url}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    logger = getLogger(__name__)

    logger.info("Starting direct message watcher...")

    client = Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_TOKEN_SECRET,
    )

    schedule.every(30).minutes.do(task)

    while True:
        schedule.run_pending()
        time.sleep(1)
