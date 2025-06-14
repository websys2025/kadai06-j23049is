#取得したデータの種類：鉄道輸送統計調査 旅客人キロ 路線別
#https://www.e-stat.go.jp/stat-search/database?page=1&layout=datalist&toukei=00600350&tstat=000001011026&cycle=8&tclass1val=0
#https://www.e-stat.go.jp/dbview?sid=0003440038
#APIリクエストURL JSON形式
#取得データ⇒表章項目：旅客人キロ,路線：新幹線_東海道線,定期・定期外：計,年度次：2020年度・2021年度・2022年度・2023年度
#http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?cdCat01=290&cdTab=140&cdCat02=100&appId=&lang=J&statsDataId=0003440038&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0

#データの使い方
#APIリクエストを送信してJSONデータを取得
#統計データの「DATA_INF」部分から必要なデータ「新幹線_東海道線」を抽出
#取得したデータをpandasのDataFrameに変換
#メタ情報を利用し、カテゴリの数値を名称に変換

import requests
import pandas as pd

APP_ID = "0cd8135c0334a94ff93349bbf379ced7bbfc50f5"
#エンドポイント
API_URL  = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

#機能
params = {
    "appId": APP_ID,
    "statsDataId":"0003440038", #「鉄道輸送統計調査 旅客人キロ 路線別」を指定
    "cdCat01":"290", #「新幹線_東海道線」を指定
    "cdTab":"140", #「旅客人キロ」を取得
    "cdCat02":"100", #「定期・定期外の計」を取得
    "metaGetFlg":"Y", #メタ情報を取得
    "lang": "J"  #日本語を指定
}

response = requests.get(API_URL, params=params)
# Process the response
data = response.json()

# 統計データからデータ部取得
values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']

# JSONからDataFrameを作成
df = pd.DataFrame(values)

# メタ情報取得
meta_info = data['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']

# 統計データのカテゴリ要素をID(数字の羅列)から、意味のある名称に変更する
for class_obj in meta_info:

    # メタ情報の「@id」の先頭に'@'を付与した文字列が、統計データの列名と対応している
    column_name = '@' + class_obj['@id']

    # 統計データの列名を「@code」から「@name」に置換するディクショナリを作成
    id_to_name_dict = {}
    if isinstance(class_obj['CLASS'], list):
        for obj in class_obj['CLASS']:
            id_to_name_dict[obj['@code']] = obj['@name']
    else:
        id_to_name_dict[class_obj['CLASS']['@code']] = class_obj['CLASS']['@name']

    # ディクショナリを用いて、指定した列の要素を置換
    df[column_name] = df[column_name].replace(id_to_name_dict)

# 統計データの列名を変換するためのディクショナリを作成
col_replace_dict = {'@unit': '単位', '$': '値'}
for class_obj in meta_info:
    org_col = '@' + class_obj['@id']
    new_col = class_obj['@name']
    col_replace_dict[org_col] = new_col

# ディクショナリに従って、列名を置換する
new_columns = []
for col in df.columns:
    if col in col_replace_dict:
        new_columns.append(col_replace_dict[col])
    else:
        new_columns.append(col)

df.columns = new_columns
print(df)