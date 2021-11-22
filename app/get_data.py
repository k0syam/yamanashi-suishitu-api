from dataclasses import dataclass
import requests
import os
from pydantic import BaseModel

source_list = [
    {"source_name": "H24", "target_url": "https://www.pref.yamanashi.jp/taiki-sui/documents/h24fujigoko.pdf"},
]

class AllData(BaseModel):
    source_list: list = source_list
    item_list: list

    def update_all_sources(self):
        for source in self.source_list:
            url =  source["target_url"]
            source_name =  source["source_name"]
            self.download_file_if_needed(url, source_name + ".pdf")

    def download_file_if_needed(self, url, filename):
        """ローカルにデータファイルがない場合は、データファイルをダウンロードする"""
        dir = os.path.dirname(__file__)
        file_path = dir + "/" + filename
        if not os.path.exists(file_path):
            data = requests.get(url).content
            with open(file_path ,mode='wb') as f:
                f.write(data)
        return file_path

class DataItem(BaseModel):
    source_name: str
    measurement_point: str
    measurement_date: str
    category: str
    value: str

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

