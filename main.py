import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL
#url = 'https://award.tabelog.com/hyakumeiten/ramen_tokyo'
#url = 'https://award.tabelog.com/hyakumeiten/ramen_osaka'
#url = 'https://award.tabelog.com/hyakumeiten/ramen_east'
url = 'https://award.tabelog.com/hyakumeiten/ramen_west'

# リクエストを送信してHTMLを取得
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 店舗情報の抽出
shops = []
for shop_item in soup.find_all('div', class_='hyakumeiten-shop__item'):
    name = shop_item.find('div', class_='hyakumeiten-shop__name').text.strip()
    area = shop_item.find('div', class_='hyakumeiten-shop__area').text.strip()
    
    # 定休日を安全に取得
    holiday_tag = shop_item.find('div', class_='hyakumeiten-shop__holiday')
    holiday = holiday_tag.text.strip() if holiday_tag else '不明'
    
    shop_url = shop_item.find('a', class_='hyakumeiten-shop__target')['href']
    
    # データをリストに追加
    shops.append([name, area, holiday, shop_url])

# データフレームに変換
df = pd.DataFrame(shops, columns=['店名', 'エリア', '定休日', 'リンク'])

# 住所を取得する関数
def get_address_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        address_element = soup.find('p', class_='rstinfo-table__address')
        if address_element:
            return address_element.text.strip()
        else:
            return '住所が見つかりませんでした'
    except Exception as e:
        return f'エラー: {e}'

# 各URLに対して住所を取得し、新しい列を作成
df['住所'] = df['リンク'].apply(get_address_from_url)

# 少し待機（サーバーへの負荷を軽減するため）
time.sleep(1)

# CSVに保存
#df.to_csv('tabelog_ramen_tokyo_with_address.csv', index=False)
#df.to_csv('tabelog_ramen_osaka_with_address.csv', index=False)
#df.to_csv('tabelog_ramen_east_with_address.csv', index=False)
df.to_csv('tabelog_ramen_west_with_address.csv', index=False)

print("スクレイピング完了。住所を含むCSVに保存しました。")
