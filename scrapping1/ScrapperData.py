import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time
import pathlib

def scrape_news():
    url = "https://www.republika.co.id/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception if request is not successful
        soup = BeautifulSoup(response.content, "lxml")
    except requests.exceptions.RequestException as e:
        print(f"Error while scraping news: {e}")
        return []
    
    news_items = soup.find_all("li", class_="list-group-item list-border conten1")
    news_data = []

    for item in news_items:
        title = item.h3.text.strip()
        category = item.find("span", class_="kanal-info").text.strip()
        publish_time_str1 = item.find('div', class_ = 'date').text.split('-')
        publish_time_str = publish_time_str1[1].strip()

        scrape_time = datetime.now()
        publish_time = datetime.strptime(publish_time_str, "%d %B %Y, %H:%M")
        time_diff = scrape_time - publish_time

        if time_diff.days > 0:
            time_ago = f"{time_diff.days} hari yang lalu"
        elif time_diff.seconds // 3600 > 0:
            time_ago = f"{time_diff.seconds // 3600} jam yang lalu"
        elif time_diff.seconds // 60 > 0:
            time_ago = f"{time_diff.seconds // 60} menit yang lalu"
        elif time_diff.seconds % 60 > 0:
            time_ago = f"{time_diff.seconds % 60} detik yang lalu"
            
        news_hash = hash((title, publish_time_str))
        
        news_info = {
            "judul": title,
            "kategori": category,
            "waktu_publish": f"{time_ago}\n{publish_time_str}",
            "waktu_scraping": scrape_time.strftime("%H:%M:%S\n%A, %d %B %Y"),
            "hash_code": news_hash,
            "waktu_real_publish" : publish_time.isoformat(),
        }
        news_data.append(news_info)

    return news_data

def save_to_json(data, filename="data.json"):
    try:
        data_dir = pathlib.Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / filename

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        # Temukan item berita yang belum ada
        new_data = [item for item in data if item["hash_code"] not in [x["hash_code"] for x in existing_data]]

        # Tambahkan data baru ke data yang sudah ada
        all_data = existing_data + new_data
        
        # Mengurutkan data sebelum disimpan
        sorted_data = sorted(all_data, key=lambda x: x['waktu_real_publish'], reverse=True)

        # Simpan semua data ke file JSON
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(new_data)} new news items to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

if __name__ == "__main__":
    while True:
        news_data = scrape_news()
        save_to_json(news_data)
        # print("Waiting 1 minutes before scraping again...")
        # time.sleep(600)  # Wait 10 minutes before scraping again