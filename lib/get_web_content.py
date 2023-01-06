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
    markdown_content = markdownify_content(html_content)
    cleansed_content = cleansing_text_to_feed(markdown_content)

    p = ProcessedContent(
        title=title,
        html_content=html_content,
        markdown_content=markdown_content,
        cleansed_content=cleansed_content,
    )

    return p


def markdownify_content(html_content: str) -> str:
    """Convert HTML-formatted content to markdown-formatted one.

    Parameters
    ----------
    html_content : str
        HTML-formatted content
    Returns
    -------
    str
        Markdown-formatted content
    """
    markdown_content = md(html_content, heading_style="ATX")
    markdown_content = re.sub(
        pattern=r"(\#\s\n)",
        repl="# ",
        string=markdown_content,
    )

    return markdown_content


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
