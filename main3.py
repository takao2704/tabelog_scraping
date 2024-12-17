import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 店舗リストのスクレイピング共通関数
def scrape_store_list(base_url, page=None):
    url = base_url.replace("${page}", str(page)) if page else base_url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    store_data = []
    
    if "hyakumeiten" in url:  # 百名店のスクレイピング処理
        stores = soup.find_all('div', class_='hyakumeiten-shop__item')
        for store in stores:
            name = store.find('div', class_='hyakumeiten-shop__name').text.strip()
            area = store.find('div', class_='hyakumeiten-shop__area').text.strip()
            holiday_tag = store.find('div', class_='hyakumeiten-shop__holiday')
            holiday = holiday_tag.text.strip() if holiday_tag else '不明'
            detail_url = store.find('a', class_='hyakumeiten-shop__target')['href']
            store_data.append({"店名": name, "エリア": area, "定休日": holiday, "リンク": detail_url})
    else:  # 一般ランキングのスクレイピング処理
        stores = soup.select(".list-rst")
        for store in stores:
            name = store.select_one(".list-rst__rst-name-target").text
            area = store.select_one(".list-rst__area-genre").text.strip().split(" / ")[0]
            holiday = store.select_one(".list-rst__holiday-text").text if store.select_one(".list-rst__holiday-text") else "不明"
            detail_url = store.get("data-detail-url")
            store_data.append({"店名": name, "エリア": area, "定休日": holiday, "リンク": detail_url})
    
    return store_data

# 店舗詳細ページから住所を取得する関数
def scrape_store_address(detail_url):
    try:
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.text, "html.parser")
        address = soup.select_one(".rstinfo-table__address").text.strip() if soup.select_one(".rstinfo-table__address") else "不明"
        return address
    except Exception as e:
        return f"エラー: {e}"

# データフレームを保存する関数
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"データをCSVに保存しました: {filename}")

# 百名店用の処理
def scrape_hyakumeiten(url, output_filename):
    print("百名店をスクレイピングしています...")
    store_data = scrape_store_list(url)
    
    for store in store_data:
        store["住所"] = scrape_store_address(store["リンク"])
        time.sleep(1)  # サーバー負荷軽減のための待機
    
    save_to_csv(store_data, output_filename)

# 特定地域ランキング用の処理
def scrape_ranking(base_url, pages, output_filename):
    print("ランキングをスクレイピングしています...")
    all_store_data = []
    
    for page in range(1, pages + 1):
        store_list = scrape_store_list(base_url, page)
        for store in store_list:
            store["住所"] = scrape_store_address(store["リンク"])
            time.sleep(1)  # サーバー負荷軽減のための待機
        all_store_data.extend(store_list)
    
    save_to_csv(all_store_data, output_filename)

if __name__ == "__main__":
    # 百名店のURL（東京、大阪、東、または西から選択）
    hyakumeiten_url = 'https://award.tabelog.com/hyakumeiten/ramen_west'
    # ランキングのベースURL（ページ番号に置換文字列を使用）
    ranking_base_url = "https://tabelog.com/kochi/rstLst/ramen/${page}/?Srt=D&SrtT=rt&sort_mode=1"
    
    # 百名店のスクレイピングを実行
    scrape_hyakumeiten(hyakumeiten_url, "hyakumeiten_data.csv")
    
    # ランキングのスクレイピングを実行
    scrape_ranking(ranking_base_url, 3, "ranking_data.csv")

