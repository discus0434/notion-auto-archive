# notion-auto-archive

<p align="center">
  <img src="https://storage.googleapis.com/zenn-user-upload/5489a48f5133-20230106.png" width=80%>
</p>

## Installation

1. NotionとTwitterのアクセストークンを取得する
2. Notionにデータベースのページを作成してIDを控える(コネクトも追加しておく）
3. `git clone`
4. `docker build` (環境によってCUDAのバージョンは変えたほうがいいかも)
5. `config/config.py`を参考にしながら`.env`にTwitterとNotionのアクセストークンとかNotionのデータベースIDとかを書く
6. `config/config.py`の`CANDIDATE_LABELS`を好みで書き換える
7. `./start_watcher.sh &`
