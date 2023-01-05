import json
import os
import subprocess
from pathlib import Path


def markdown_to_notion(
    javascript_path: Path,
    json_path: Path,
    markdown_content: str,
) -> dict:
    """Convert markdown content to notion-compatible format of the content.
    This function actually just calls the javascript script.

    Parameters
    ----------
    javascript_path : Path
        javascript script path to call
    json_path : Path
        json file path to save the result
    markdown_content : str
        markdown content to convert

    Returns
    -------
    dict
        notion-compatible format of the content.
    """
    subprocess.run(
        ["node", javascript_path.absolute(), markdown_content, json_path.absolute()]
    )

    with open(json_path, "r") as f:
        notioned_content = json.load(f)

    os.remove(json_path.absolute())

    return notioned_content
