from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import arxiv
import pdf2image
from bs4 import BeautifulSoup
from markdownify import markdownify
from transformers import pipeline


@dataclass
class ProcessedContent:
    title: str
    url: str
    html_content: str
    markdown_content: str
    notion_content: list
    cleansed_content: str
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
        translator = pipeline("translation", model="staka/fugumt-en-ja")
        translated_abstract = translator(info.summary)[0]["translation_text"]
        del translator

        subprocess.run(
            ["/bin/bash", "scripts/arxiv-download.sh", arxiv_id, cache_path.absolute()],
            timeout=100,
        )

        for root, dirs, files in os.walk(top=cache_path.absolute()):
            for file in files:
                if file.endswith(".pdf"):
                    path = Path(os.path.join(root, file))
                    image = pdf2image.convert_from_path(path)
                    image[0].save(path.with_suffix(".png"), "PNG")

                if file.endswith(".tex"):
                    path = Path(os.path.join(root, file))
                    with open(path, "r") as f:
                        text = f.read()

                    if ".pdf" in text:
                        # replace .pdf with .png and save
                        text = text.replace(".pdf", ".png")
                        with open(path, "w") as f:
                            f.write(text)

        subprocess.run(
            [
                "docker",
                "exec",
                "engrafo",
                "engrafo",
                "output/",
                "output/",
            ],
            timeout=1000,
            stdout=subprocess.DEVNULL,
        )
        html = open("/home/workspace/notion-auto-archive/content/index.html").read()
        soup = BeautifulSoup(html, "html.parser")

        figures = []
        for fig in soup.find_all("figure"):
            figure = {}
            if not len(fig.find_all("td")) > 0:
                for img, caption in zip(
                    fig.find_all("img"), fig.find_all("figcaption")
                ):
                    figures.append({"img": img, "caption": caption.text})

        html_figures = []
        for figure in figures:
            html_figures.append(
                f"""
                <span>
                    {str(figure["img"])}
                    <p>{figure["caption"]}</p>
                </span>
                """
            )

        html_content = f"""
            <html>
                <body>
                    <h2>Abstract</h2>
                        <p>{translated_abstract}</p>
                    <h2>Figures</h2>
                    <div>
                        {''.join(list(map(
                            lambda x: f"<section>{str(x)}</section>", html_figures
                        )))}
                    </div>
                </body>
            </html>
            """

        title = info.title
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

    with open(cache_path.absolute() / "content.json", "r") as f:
        notion_content = json.load(f)

    if url.startswith("https://arxiv.org/"):
        cleansed_content = info.summary.replace("\n", " ")
        tags = [
            arxiv_categories[info.categories[i]] for i in range(len(info.categories))
        ]
    else:
        cleansed_content = cleansing_text_to_feed(markdown_content)
        tags = None

    return ProcessedContent(
        title=title,
        url=url,
        html_content=html_content,
        markdown_content=markdown_content,
        cleansed_content=cleansed_content,
        notion_content=notion_content,
        tags=tags,
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

    text.replace("???", " ").replace("???", "(").replace("???", ")")

    # substitute spaces 2 or more than 2 times to 1 space
    text = re.sub(
        pattern=r"\s{2,}",
        repl=" ",
        string=text,
    )

    if len(text) > 2048:
        # truncate the sentence to approx. 2048 characters
        # end with a period or "???".
        try:
            if "???" in text[:2048]:
                text = text[:2048].rsplit("???", 1)[0] + "???"
            else:
                text = text[:2048].rsplit(".", 1)[0] + "."
        except Exception:
            text = text[:2048]

    return text
