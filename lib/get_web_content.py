from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import arxiv
from markdownify import markdownify


@dataclass
class ProcessedContent:
    title: str
    url: str
    notion_content: list
    cleansed_content: str | None = None
    tags: list[str] | None = None


def get_web_content(
    url: str,
    cache_path: Path,
    arxiv_categories: dict[str, str],
) -> ProcessedContent:
    """Get web page of the URL & process it to 5 types of contents as follows:
    1. title of the web page
    2. url of the web page
    3. html-formatted one, which is extracted by readability
    4. markdown-formatted one
    5. notion-compatible one
    6. cleansed one
    7. tags, which is given only when the URL is arXiv at the moment

    Parameters
    ----------
    url : str
        URL of the web page
    cache_path : Path
        Path to the cache directory
    arxiv_categories : dict[str, str]
        Dictionary of arXiv categories.
        e.g. {"cs.AI": "artificial intelligence"}
    Returns
    -------
    ProcessedContent
        Processed content of the web page, explained above.
    """
    if url.startswith("https://arxiv.org/"):
        arxiv_id = url.split("/")[-1]
        info = next(arxiv.Search(id_list=[arxiv_id]).results())
        info.download_pdf(cache_path.absolute().__str__(), filename=arxiv_id + ".pdf")

        subprocess.run(
            [
                "docker",
                "exec",
                "pdf-reader",
                "python",
                "puddle.py",
                "--pdf_path",
                f"/home/workspace/pdf-reader/output/{arxiv_id}.pdf",
                "--out_path",
                "/home/workspace/pdf-reader/output/",
            ],
            timeout=3600,
            stdout=subprocess.DEVNULL,
        )

        markdown_content = " ".join(
            [f"![{i}.png]({path})" for i, path in enumerate(sorted(cache_path.glob("*.png")))]
        )

        with open(cache_path.absolute() / "content.md", "w") as f:
            f.write(markdown_content)

        subprocess.run(
            [
                "node",
                "js/markdown_to_notion.js",
                cache_path.absolute() / "content.md",
                cache_path.absolute() / "content.json",
            ]
        )

        with open(cache_path.absolute() / "content.json", "r") as f:
            notion_content = json.load(f)

        return ProcessedContent(
            title=info.title,
            url=url,
            notion_content=notion_content,
            tags=[
                arxiv_categories[info.categories[i]]
                for i in range(len(info.categories))
            ],
        )
    else:
        subprocess.run(
            ["node", "js/readable.js", url, cache_path.absolute() / "readable.json"]
        )

        with open(cache_path.absolute() / "readable.json", "r") as f:
            ret = json.load(f)

        title = ret["title"]
        html_content = ret["content"]

        markdown_content = markdownify(
            html_content, heading_style="ATX", escape_underscores=False
        )
        markdown_content = re.sub(
            pattern=r"(\#\s\n)",
            repl="# ",
            string=markdown_content,
        )

        with open(cache_path.absolute() / "content.md", "w") as f:
            f.write(markdown_content)

        subprocess.run(
            [
                "node",
                "js/markdown_to_notion.js",
                cache_path.absolute() / "content.md",
                cache_path.absolute() / "content.json",
            ]
        )

        cleansed_content = cleansing_text_to_feed(markdown_content)

        with open(cache_path.absolute() / "content.json", "r") as f:
            notion_content = json.load(f)

        return ProcessedContent(
            title=title,
            url=url,
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

    if len(text) > 2048:
        # truncate the sentence to approx. 2048 characters
        # end with a period or "。".
        try:
            if "。" in text[:2048]:
                text = text[:2048].rsplit("。", 1)[0] + "。"
            else:
                text = text[:2048].rsplit(".", 1)[0] + "."
        except Exception:
            text = text[:2048]

    return text
