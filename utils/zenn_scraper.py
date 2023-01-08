import time

from tqdm import tqdm
import pandas as pd
import requests
from bs4 import BeautifulSoup

from lib import get_web_content
from config import (
    JAVASCRIPT_PATH,
    JSON_PATH,
)


def main():
    li = []
    try:
        for i in tqdm(range(1, 100)):
            try:
                url = f"https://zenn.dev/articles?page={i}"
                res = requests.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                entries = soup.find_all("div", class_="ArticleList_content__i6AQy")

                for entry in entries:

                    inner_url = f"https://zenn.dev{entry.find('a', class_='ArticleList_link__vf_6E')['href']}"

                    try:
                        num_likes = entry.find(
                            "span", class_="ArticleList_like__c4148"
                        ).text
                    except AttributeError:
                        continue

                    if int(num_likes) < 10:
                        continue

                    res_inner = requests.get(inner_url)
                    inner_soup = BeautifulSoup(res_inner.text, "html.parser")

                    tags = []
                    for element in inner_soup.find_all(
                        "div", class_="View_topicName__rxKth"
                    ):
                        tags.append(element.text)

                    p = get_web_content(
                        url=inner_url,
                        javascript_path=JAVASCRIPT_PATH,
                        json_path=JSON_PATH,
                    )

                    d = pd.DataFrame(
                        [
                            {
                                "title": p.title,
                                "tags": tags,
                                "cleansed_content": p.cleansed_content,
                                "url": inner_url,
                            }
                        ]
                    )
                    li.append(d)

                    time.sleep(20)

                time.sleep(20)

            except Exception as e:
                print(e)
                time.sleep(100)
                continue

        df = pd.concat(li, axis=0, ignore_index=True)

    except KeyboardInterrupt as e:
        df = pd.concat(li, axis=0, ignore_index=True)

    df.to_json("zenn.json", orient="records", force_ascii=False)


if __name__ == "__main__":
    main()
