from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessedContent:
    title: str
    html_content: str
    markdown_content: str
    notion_content: list
    cleansed_content: str


def get_web_content(
    url: str, javascript_path: Path, json_path: Path
) -> ProcessedContent:
    """Get web page of the URL & process it to 5 types of contents as follows:
    1. title of the web page
    2. html-formatted one, which is extracted by readability
    3. markdown-formatted one
    4. notion-compatible one
    5. cleansed one

    Parameters
    ----------
    url : str
        URL of the web page
    Returns
    -------
    ProcessedContent
        Processed content of the web page, explained above.
    """
    subprocess.run(["node", javascript_path.absolute(), url, json_path.absolute()])
    with open(json_path, "r") as f:
        ret = json.load(f)
    os.remove(json_path.absolute())
    title = ret["article"]["title"]
    html_content = ret["article"]["content"]
    markdown_content = ret["markdown"]
    cleansed_content = cleansing_text_to_feed(markdown_content)
    notion_content = ret["blocks"]

    return ProcessedContent(
        title=title,
        html_content=html_content,
        markdown_content=markdown_content,
        cleansed_content=cleansed_content,
        notion_content=notion_content,
    )


def cleansing_text_to_feed(text: str) -> str:
    # remove texts between | and | or - and -, but \n is between them, do not remove
    text = re.sub(
        pattern=r"(\|.*[^\n].*\|)|(\-.\n.*\-)",
        repl=" ",
        string=text,
    )

    # remove [ and ], \n, \r, \t, and multiple spaces
    text = re.sub(
        pattern=r"(\n)|(\r)|(\t)|(\s{2,})|(\[)|(\])",
        repl=" ",
        string=text,
    )

    # remove https://... or http://... or (https://...) or (http://...)
    text = re.sub(
        pattern=r"\(?https?://[^\s]+\)?",
        repl="",
        string=text,
    )

    # remove texts between ``` and ```
    text = re.sub(
        pattern=r"(```.*?```)",
        repl=" ",
        string=text,
    )

    text.replace("　", " ").replace("（", "(").replace("）", ")")

    # substitute spaces 2 or more than 2 times to 1 space
    text = re.sub(
        pattern=r"\s{2,}",
        repl=" ",
        string=text,
    )

    return text
