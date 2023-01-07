from lib import ProcessedContent
from notion_client import Client


def post_to_notion(
    access_token: str,
    database_id: str,
    processed_content: ProcessedContent,
    tags: list[str],
    url: str,
) -> None:
    """Post content to Notion.

    Parameters
    ----------
    access_token : str
        notion access token. this is given by environment variable.
    database_id : str
        database id of the notion. this is given by environment variable.
    processed_content : ProcessedContent
        processed content of web page.
    tags : list[str]
        list of tags given to the content.
    url : str
        url of the content.
    """
    notion = Client(auth=access_token)

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

    for block in processed_content.notion_content:
        notion.blocks.children.append(block_id=db["id"], children=[block])
