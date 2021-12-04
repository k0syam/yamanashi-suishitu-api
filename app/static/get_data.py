import datetime
from dataclasses import dataclass
import math
import requests
import os
import pandas as pd
import pickle
from pydantic import BaseModel
import tabula
from tika import parser
from app.static.dataitem import DataItem

# ソースリスト一覧
# 公開されているURLをもとにデータ追加を随時行う
source_list = [
    {
        "source_name": "H24",
        "target_url": "https://www.pref.yamanashi.jp/taiki-sui/documents/h24fujigoko.pdf",
    },
]

# データハンドリングを行うクラス
class AllData(BaseModel):
    source_list: list = source_list

    def update_all_sources(self, update_all=True):
        """source_listに基づいてすべてのデータを取得・更新する

        Args:
            update_all (bool, optional): .dataitemの有無にかかわらずすべてアップデートするかどうか. Defaults to True.
        """
        for source in self.source_list:
            url = source["target_url"]
            source_name = source["source_name"]
            self.download_file_if_needed(url, source_name + ".pdf")
            self.update_dataitem(source_name, update_all=update_all)

    def update_dataitem(self, source_name: str, update_all=True):
        """特定のソースから.dataitemを出力する

        Args:
            source_name (str): ソース名
            update_all (bool, optional): .dataitemの有無にかかわらずすべてアップデートするかどうか. Defaults to True.
        """
        dir = os.path.dirname(__file__)
        pdf_path = dir + "/" + source_name + ".pdf"
        dataitem_path = dir + "/" + source_name + ".dataitem"
        if not os.path.exists(dataitem_path) or update_all:
            for source in self.source_list:
                if source_name in source["source_name"]:
                    dir = os.path.dirname(__file__)
                    file_path = dir + "/" + source_name + ".pdf"
            file_data = parser.from_file(file_path)
            text = file_data["content"]
            measurement_points = [s for s in text.split("\n") if "水域名" in s]
            measurement_points = [
                s.split()[1] + "_" + s.split()[3] for s in measurement_points
            ]
            ret = {"areas": measurement_points}
            dataitems = []
            for i, measurement_point in enumerate(measurement_points):
                dfs = tabula.read_pdf(pdf_path, lattice=True, pages=i + 1)[0]
                for label, content in dfs.iteritems():
                    if label == "一 般 項 目":
                        index_name = content.values
                    elif "0" in label:
                        continue
                    else:
                        date_str = content.values[0] + content.values[1]
                        measurement_date = datetime.datetime.strptime(
                            date_str, "%m月%d日%H時%M分"
                        )
                        weather = content.values[2]
                        for category, value in zip(index_name[3:], content.values[3:]):
                            if type(value) == str:
                                dataitem = DataItem(
                                    source_name=source_name,
                                    measurement_point=measurement_point,
                                    measurement_date=measurement_date,
                                    weather=weather,
                                    category=category,
                                    value=value,
                                )
                                dataitems.append(dataitem)
            ret["dataitems"] = dataitems
            with open(dataitem_path, "wb") as f:
                pickle.dump(ret, f, -1)

    def download_file_if_needed(self, url: str, filename: str):
        """ローカルにデータファイルがない場合は、データファイルをダウンロードする

        Args:
            url (str): PDFダウンロード先のURL
            filename (str): 保存ファイル名

        Returns:
            file_path (pathlib.Path): 保存したファイル名
        """
        dir = os.path.dirname(__file__)
        file_path = dir + "/" + filename
        if not os.path.exists(file_path):
            data = requests.get(url).content
            with open(file_path, mode="wb") as f:
                f.write(data)
        return file_path

    def obtain_dataitem_static(self, source_name: str):
        """生成済みの.dataitemを読み込んでlistとして返す

        Args:
            source_name (str): 参照するソース名(ex. H24)

        Returns:
            ret: .dataitemを保有するlist
        """
        dir = os.path.dirname(__file__)
        dataitem_path = dir + "/" + source_name + ".dataitem"
        with open(dataitem_path, "rb") as f:
            ret = pickle.load(f)
        return ret


if __name__ == "__main__":
    all_data = AllData()
    all_data.update_all_sources()
