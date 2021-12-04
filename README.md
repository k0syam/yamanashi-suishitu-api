# yamanashi-suishitsu-api
山梨県公共用水域水質測定結果取得API(Under developing)

# APIの内容
## /
* 保有データしているソースの一覧を取得する
## /source/{source_name}
* そのソースに記載のある測定地点の一覧を取得する
## /source/{source_name}/area/{area_name}
* 指定したソース・測定地点の測定結果一覧を取得する

# 運用方法
## 実行環境を構築する
* Python 3.7以上をインストールする
* Java Runtimeをインストールする(tabula)
* リポジトリをダウンロードする．実行フォルダへ移動する
* venvで仮想環境を作成・モジュールインストールを行う
    * ex. `python3 -m venv env` -> `source env/bin/activate` -> `pip install -r requirements.txt`
* uvicornからテスト環境での動作確認を行う`uvicorn app.main:app --reload`
## ソースを追加する・データを更新する
* app/static/get_data.py内のsource_listへsource_name・URLを追加する
* データを更新する: `python -m app.static.get_data`
    * static内に.pdfファイルと.dataitemファイルが生成される

# 参照プロジェクト
* [山梨県オープンデータAPIプロジェクト](https://github.com/opendata-yamanashi)
* [Singen.py FAST API](https://github.com/shingenpy/fastapi_workshop)