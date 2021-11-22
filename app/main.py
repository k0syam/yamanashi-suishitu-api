from typing import Optional
from fastapi import FastAPI
import pandas as pd
import tabula
from tika import parser
import json
import os
from . import get_data

root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(
    title="公共用水域水質測定結果API",
    root_path=root_path
)

@app.get("/")
def read_source():
    """ 取得データソースの略称とURLの一覧を取得する

    Returns:
        json: source_list一覧
    """
    all_data = get_data.AllData()
    ret = {"source": all_data.source_list}
    return ret

@app.get("/source/{source_name}")
def read_area(source_name: str):
    """特定のソース（採取年）から水域一覧を取得する

    Args:
        source_name (str): ソースの年キーワード

    Returns:
        [type]: [description]
    """
    all_data = get_data.AllData()
    for source in all_data.source_list:
        if source_name in source["source_name"]:
            dir = os.path.dirname(__file__)
            file_path = dir + "/" + source_name + ".pdf"
            print(file_path)
    file_data = parser.from_file(file_path)
    text = file_data["content"]
    regions = [s for s in text.split("\n") if "水域名" in s]
    regions = [s.split()[1] for s in regions]
    ret = {"areas": regions}
    return ret

@app.get("/source/{source_name}/area/{area}")
def read_data(source_name: str, area: str):
    """特定ソース・水質採取エリアの水質調査結果一覧を取得する

    Args:
        source_name (str): [description]
        area (str): [description]

    Returns:
        [type]: [description]
    """
    all_data = get_data.AllData()
    for source in all_data.source_list:
        if source_name in source["source_name"]:
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
