import requests
from bs4 import BeautifulSoup
import pandas as pd

# ランキングサイトから店舗のリストを取得する関数
def scrape_store_list(base_url, page):
    url = base_url.replace("${page}", str(page))  # ページ番号を置換
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 店舗情報をリストに保存
    store_data = []
    stores = soup.select(".list-rst")  # 店舗情報のセレクタ
    
    for store in stores:
        store_name = store.select_one(".list-rst__rst-name-target").text
        area = store.select_one(".list-rst__area-genre").text.strip().split(" / ")[0]  # エリア情報の分割
        holiday = store.select_one(".list-rst__holiday-text").text if store.select_one(".list-rst__holiday-text") else "不明"
        detail_url = store.get("data-detail-url")  # 店舗の詳細URL
        
        store_data.append({
            "店名": store_name,
            "エリア": area,
            "定休日": holiday,
            "リンク": detail_url
        })
    
    return store_data

# 店舗の詳細ページから住所を取得する関数
def scrape_store_address(detail_url):
    response = requests.get(detail_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 住所の取得
    address = soup.select_one(".rstinfo-table__address").text.strip() if soup.select_one(".rstinfo-table__address") else "不明"
    return address

# メイン処理
def main():
    base_url = "https://tabelog.com/akita/rstLst/ramen/${page}/?Srt=D&SrtT=rt&sort_mode=1"
    
    all_store_data = []

    # ページ1から3まで繰り返し
    for page in range(1, 4):
        store_list = scrape_store_list(base_url, page)
        
        # 各店舗の詳細ページから住所を取得
        for store in store_list:
            store["住所"] = scrape_store_address(store["リンク"])
            all_store_data.append(store)

    # データをCSVに保存
    df = pd.DataFrame(all_store_data)
    df.to_csv("store_data_akita.csv", index=False, encoding="utf-8-sig")

    print("データをCSVに保存しました。")

if __name__ == "__main__":
    main()
