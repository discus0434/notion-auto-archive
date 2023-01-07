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
                url = f"https://qiita.com/search?q=stocks%3A>100&sort=created&stocked=&page={i}"
                res = requests.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                entries = soup.find_all("article", class_="style-ocoetd")

                for entry in entries:
                    t = entry.find("h1", class_="style-1l1igte")
                    inner_url = f"https://qiita.com{t.find('a').get('href')}"

                    tags = [
                        tag.text
                        for tag in entry.find("div", class_="style-f38rbf")
                        .find("div", class_="style-1j7ce6v")
                        .find_all("a")
                    ]

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
                    time.sleep(10)
            except Exception as e:
                print(e)
                time.sleep(100)
                continue

        df = pd.concat(li, axis=0, ignore_index=True)

    except KeyboardInterrupt as e:
        df = pd.concat(li, axis=0, ignore_index=True)

    df.to_json("qiita.json", orient="records", force_ascii=False)


if __name__ == "__main__":
    main()
