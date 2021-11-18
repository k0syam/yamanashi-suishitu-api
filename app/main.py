from typing import Optional
from fastapi import FastAPI
import requests
import pandas as pd
import tabula
from tika import parser
import json
import os

source_list = [
    {"year": "H24", "target_url": "https://www.pref.yamanashi.jp/taiki-sui/documents/h24fujigoko.pdf"},
]

root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(
    title="公共用水域水質測定結果API",
    root_path=root_path
)

@app.get("/")
def read_root():
    """ 取得データ年度とURLの一覧を取得する

    Returns:
        json: source_list一覧
    """
    ret = {"source": source_list}
    return ret

@app.get("/{year}")
def read_area(year: str):
    """特定のソース（採取年）から水域一覧を取得する

    Args:
        year (str): ソースの年キーワード

    Returns:
        [type]: [description]
    """
    for source in source_list:
        if year in source["year"]:
            path = source["target_url"]
    file_data = parser.from_file(path)
    text = file_data["content"]
    regions = [s for s in text.split("\n") if "水域名" in s]
    regions = [s.split()[1] for s in regions]
    ret = {"areas": regions}
    return ret

@app.get("/{year}/{area}")
def read_data(year: str, area: str):
    """特定ソース・水質採取エリアの水質調査結果一覧を取得する

    Args:
        year (str): [description]
        area (str): [description]

    Returns:
        [type]: [description]
    """
    for source in source_list:
        if year in source["year"]:
            path = source["target_url"]
    previous_df = pd.DataFrame()
    file_data = parser.from_file(path)
    text = file_data["content"]
    regions = [s for s in text.split("\n") if "水域名" in s]
    for i, region in enumerate(regions):
        if area in region:
            dfs = tabula.read_pdf(path, lattice=True, pages = i+1)
            print(dfs)
    # データ結合
    # for df in dfs:
    #     if (check_columns(df, previous_df)):
    #         df = pd.concat([previous_df, df])
    #     previous_df = df
    # return previous_df
    return dfs


# @app.get("/area/{area}")
# def read_item(area: str):
#     data = get_data(target_url)
#     df_mask = data['市町村名'] == area
#     data = data[df_mask]
#     json_data = data.to_json(orient = 'records')
#     return json.loads(json_data)

def get_data(url):
    path = download_file_if_needed(url)

    previous_df = pd.DataFrame()
    file_data = parser.from_file(path)
    text = file_data["content"]
    regions = [s for s in text.split("\n") if "水域名" in s]
    for i, s in enumerate(regions):
        dfs = tabula.read_pdf(path, lattice=True, pages = i+1)
        # print(type(dfs[0]))
        dfs = [d.insert("水域名")]
    # データ結合
    for df in dfs:
        if (check_columns(df, previous_df)):
            df = pd.concat([previous_df, df])
        previous_df = df
    
    return previous_df

def check_columns(df, previous_df):
    """前ページと現ページのデータフレーム比較"""
    diff1 = set(df.keys()) - set(previous_df.keys())
    diff2 = set(previous_df.keys()) - set(df.keys())
    return (len(diff1) == 0 and len(diff2) == 0)

def download_file_if_needed(url, filename="data.pdf"):
    """ローカルにデータファイルがない場合は、データファイルをダウンロードする"""
    dir = os.path.dirname(__file__)
    file_path = dir + "/" + filename
    if not os.path.exists(file_path):
        data = requests.get(url).content
        with open(file_path ,mode='wb') as f:
            f.write(data)

    return file_path
