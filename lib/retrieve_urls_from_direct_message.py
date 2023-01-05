from __future__ import annotations

import requests
import tweepy


def retrieve_urls_from_direct_message(
    client: tweepy.Client,
    user_name: str | None = None,
    user_id: str | None = None,
    num_retrieves: int = 5,
) -> list[str]:
    """Retrieve URLs from direct messages.

    Parameters
    ----------
    client : tweepy.Client
    user_name : str | None, optional
    user_id : str | None, optional
    num_retrieves : int, optional


    Returns
    -------
    list[str] : List of URLs which are retrieved from direct messages.

    """
    if user_id is None:
        user_id = client.get_user(username=user_name).data["id"]

    direct_messages = client.get_direct_message_events(
        participant_id=user_id,
        max_results=num_retrieves,
    )

    urls = []
    for message in direct_messages.data:

        if not message.text.startswith("http"):
            continue

        url = requests.get(message.text).url
        urls.append(url)

    return urls
