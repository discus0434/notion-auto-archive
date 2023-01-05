from __future__ import annotations

import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from readability import Document


@dataclass
class ProcessedContent:
    title: str
    html_content: str
    markdown_content: str
    cleansed_content: str


def get_web_content(url: str) -> ProcessedContent:
    """Get web page of the URL & process it to 4 types of contents as follows:
    1. title of the web page
    2. html-formatted one, which is extracted by readability
    3. markdown-formatted one, which is extracted by readability
    4. cleansed one, which is extracted by readability

    Parameters
    ----------
    url : str
        URL of the web page
    Returns
    -------
    ProcessedContent
        Processed content of the web page, explained above.
    """
    ret = requests.get(url)
    return process_content(ret)


def process_content(ret: requests.Response) -> ProcessedContent:
    title = BeautifulSoup(ret.text, "html.parser").title.string
    html_content = Document(ret.text).summary()
    markdown_content = md(html_content)
    cleansed_content = cleansing_text_to_feed(
        BeautifulSoup(html_content, "html.parser").text
    )

    p = ProcessedContent(
        title=title,
        html_content=html_content,
        markdown_content=markdown_content,
        cleansed_content=cleansed_content,
    )

    return p


def cleansing_text_to_feed(text: str) -> str:
    text = re.sub(
        pattern=r"(\[.*?\])|(\(.*?\))|(\n)|(\r)|(\t)|(\s{2,})",
        repl=" ",
        string=text,
    )

    return text
