import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint as pprint
import re
import os

# 使用 GET 方式下載普通網頁
res = requests.get('https://www.gutenberg.org/browse/languages/zh')

# 伺服器回應的狀態碼
print(res.status_code)

# 回傳資料的編碼
print(res.encoding)

# 輸出網頁 HTML 原始碼
print(res.text)

soup = bs(res.text, "lxml")

#取得書籍的編號
lis = soup.select("li.pgdbetext > a[href]")
print(lis)
len(lis)

#[小實驗]試試看用正則抓書名及編號，變成一個字典

element = '<a href="/ebooks/25328">豆棚閒話</a>'

# 正則中加入：只抓中文字（value 部分限定為中文）
match = re.search(r'href="/ebooks/(\d+)">([\u4e00-\u9fff]+)</a>', element)

if match:
    key = match.group(1)      # '25328'
    value = match.group(2)    # '豆棚閒話'
    result = {key: value}
    print(result)
else:
    print("未找到符合條件的項目")

#先開一個空字典
book_dict = {}

#遍歷清單中的元素，用正則取出書的編號和書名

for element in lis:
  match = re.search(r'href="/ebooks/(\d+)">([\u4e00-\u9fff]+)</a>', str(element))
  if match:
    key = match.group(1)      # '25328'
    value = match.group(2)    # '豆棚閒話'
    book_dict[key] = value

pprint(book_dict)
len(book_dict)

# 建立儲存資料夾

output_folder = "project_gutenberg"
os.makedirs(output_folder, exist_ok=True)

for book_id, title in book_dict.items():
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}-images.html"
    print(f" 造訪：{url}")

    res = requests.get(url)
    res.raise_for_status()

    soup = bs(res.text, "html.parser")

    body = soup.body
    full_text = body.get_text(separator='\n')

   # 建立 START / END 標記
    start_marker = f"*** START OF THE PROJECT GUTENBERG EBOOK {title} ***"
    end_marker = f"*** END OF THE PROJECT GUTENBERG EBOOK {title} ***"

    # 找到起訖位置
    start_index = full_text.find(start_marker)
    end_index = full_text.find(end_marker)

    # 擷取內文區間
    body_text = full_text[start_index + len(start_marker):end_index].strip()

    # 只保留中文書名在前面
    chinese_title_only = ''.join(re.findall(r'[\u4e00-\u9fff]+', title))
    pure_text = chinese_title_only + '\n\n' + body_text

    # 如果有中文才儲存
    if re.search(r'[\u4e00-\u9fff]', pure_text):
        filename = f"{title}.txt"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(pure_text)
        print(f"已儲存：{filepath}\n")
    else:
        print(f"本書無中文內容，跳過：{title}\n")
