from __future__ import annotations

from pathlib import Path


def compare_and_save_urls(urls: list[str], urls_save_path: str | Path) -> list[str]:
    """This function does the following:
    1. Compares the given URLs with the URLs in the given file.
    2. Saves the given URLs to the given file path.

    Arguments
    ---------
        urls (str): The URLs to compare.
        urls_save_path (str | Path): The path to the file containing the URLs to compare with.

    Returns
    -------
        list[str]: The URLs that are not in the given file.
    """
    if isinstance(urls_save_path, str):
        urls_save_path = Path(urls_save_path)

    if not urls_save_path.exists():
        urls_save_path.touch()

    with open(urls_save_path, "r") as f:
        previous_urls = f.read().splitlines()

    new_urls = set(urls) - set(previous_urls)

    with open(urls_save_path, "w") as f:
        f.write("\n".join(urls))

    return list(new_urls)
