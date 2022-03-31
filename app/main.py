import datetime
from typing import Optional
from fastapi import FastAPI
import pandas as pd
import tabula
from tika import parser
import json
import os
from .static import get_data
from .static.dataitem import DataItem

root_path = os.getenv("ROOT_PATH", "")

# 全データの取得をおこなう
get_all_data = get_data.AllData()
get_all_data.update_all_sources()


app = FastAPI(title="公共用水域水質測定結果API", root_path=root_path)


@app.get("/")
def read_source():
    """取得データソースの略称とURLの一覧を取得する

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
    """
    all_data = get_data.AllData()
    areas = all_data.obtain_dataitem_static(source_name)["areas"]
    ret = {"areas": areas}
    return ret


@app.get("/source/{source_name}/area/{area}")
def read_data(source_name: str, area: str):
    """特定ソース・水質採取エリアの水質調査結果一覧を取得する

    Args:
        source_name (str): ソースの年キーワード
        area (str): 測定点のキーワード
    """
    all_data = get_data.AllData()
    areas = all_data.obtain_dataitem_static(source_name)["areas"]
    dataitems = all_data.obtain_dataitem_static(source_name)["dataitems"]
    ret = []
    for dataitem in dataitems:
        if dataitem.measurement_point == area:
            out = dataitem.__dict__
            out["measurement_date"] = out["measurement_date"].strftime("%m-%d")
            ret.append(out)
    return ret
