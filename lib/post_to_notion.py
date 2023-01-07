import json
import time
from pathlib import Path

import requests
from lib import ProcessedContent
from notion_client import Client
from tqdm import tqdm


def post_to_notion(
    notion_access_token: str,
    gyazo_access_token: str,
    database_id: str,
    processed_content: ProcessedContent,
    tags: list[str],
    url: str,
) -> None:
    """Post content to Notion.

    Parameters
    ----------
    notion_access_token : str
        notion access token. this is given by environment variable.
    gyazo_access_token : str
        gyazo access token. this is given by environment variable.
    database_id : str
        database id of the notion. this is given by environment variable.
    processed_content : ProcessedContent
        processed content of web page.
    tags : list[str]
        list of tags given to the content.
    url : str
        url of the content.
    """
    notion = Client(auth=notion_access_token)

    processed_content = organize_notion_blocks(
        processed_content=processed_content,
        access_token=gyazo_access_token,
    )

    time.sleep(10)

    db = notion.pages.create(
        **{
            "parent": {
                "type": "database_id",
                "database_id": database_id,
            },
            "properties": {
                "Name": {"title": [{"text": {"content": processed_content.title}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in tags]},
                "URL": {"url": url},
            },
        }
    )

    for block in tqdm(
        processed_content.notion_content,
        total=len(processed_content.notion_content),
        desc="Uploading blocks to notion...",
    ):
        if "rich_text" in block[block["type"]]:
            if len(block[block["type"]]["rich_text"]) >= 100:
                truncated_1 = block[block["type"]]["rich_text"][:100]
                truncated_2 = block[block["type"]]["rich_text"][100:]
                notion.blocks.children.append(
                    block_id=db["id"],
                    children=[
                        {
                            "type": block["type"],
                            block["type"]: {"rich_text": truncated_1},
                        }
                    ],
                )
                notion.blocks.children.append(
                    block_id=db["id"],
                    children=[
                        {
                            "type": block["type"],
                            block["type"]: {"rich_text": truncated_2},
                        }
                    ],
                )
                continue
        notion.blocks.children.append(block_id=db["id"], children=[block])


def organize_notion_blocks(
    processed_content: ProcessedContent,
    access_token: str,
) -> ProcessedContent:
    """Remove invalid URLs & Upload images to gyazo.

    Parameters
    ----------
    processed_content : ProcessedContent
        processed content of web page.
    access_token : str
        gyazo api key
    Returns
    -------
    ProcessedContent
        processed content of web page, which is:
            - image paths are replaced with gyazo urls
            - invalid urls are removed
    """

    def process_for_image(block: dict) -> dict:
        image_path_or_url = block["image"]["external"]["url"]

        if "gyazo" in image_path_or_url:
            return block

        if image_path_or_url.startswith("http"):
            image = requests.get(image_path_or_url).content
        else:
            image = Path(f"content/{image_path_or_url}").read_bytes()

        res = upload_image_to_gyazo(image, access_token)
        time.sleep(10)

        if res.status_code == 200:
            block["image"]["external"]["url"] = json.loads(res.text)["url"]
        elif res.status_code == 401:
            raise Exception("gyazo access token is invalid.")
        else:
            raise Exception("gyazo: unknown error occurred.")

        return block

    for i, block in enumerate(processed_content.notion_content):
        if block["type"] == "image":
            block = process_for_image(block)

        # remove invalid link if it is not http(s); such as mailto: or #bib:
        if block["type"] == "text":
            if "link" in inner_block["text"]:
                if block["text"]["link"]["url"][:4] != "http":
                    del block["text"]["link"]

        if block["type"] != "text" and block["type"] != "image":
            block_type = block["type"]
            if "rich_text" in block[block_type]:
                for inner_block in block[block_type]["rich_text"]:
                    if inner_block["type"] == "image":
                        inner_block = process_for_image(inner_block)
                    if inner_block["type"] == "text":
                        if "link" in inner_block["text"]:
                            if inner_block["text"]["link"]["url"][:4] != "http":
                                del inner_block["text"]["link"]

        if block["type"] == "table":
            processed_content.notion_content[i] = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "annotations": {
                                "bold": False,
                                "strikethrough": False,
                                "underline": False,
                                "italic": False,
                                "code": False,
                                "color": "default",
                            },
                            "text": {"content": "table"},
                        }
                    ]
                },
            }

    return processed_content


def upload_image_to_gyazo(image: bytes, access_token: str) -> requests.Response:

    files = {"imagedata": image}

    res = requests.request(
        method="post",
        url="https://upload.gyazo.com/api/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
    )

    return res
