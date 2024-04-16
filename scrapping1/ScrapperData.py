import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from dateutil.parser import parse as strptime_best
import pathlib
import hashlib

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
        # Ditambahkan pengecekan karena ternyata 'waktu publish' yang disediakan website beritanya berubah-ubah
        if 'lalu' in publish_time_str:
            time_ago = publish_time_str
        else:
            publish_time = strptime_best(publish_time_str)
            time_diff = scrape_time - publish_time

            if time_diff.days > 0:
                time_ago = f"{time_diff.days} hari yang lalu"
            elif time_diff.seconds // 3600 > 0:
                time_ago = f"{time_diff.seconds // 3600} jam yang lalu"
            elif time_diff.seconds // 60 > 0:
                time_ago = f"{time_diff.seconds // 60} menit yang lalu"
            elif time_diff.seconds % 60 > 0:
                time_ago = f"{time_diff.seconds % 60} detik yang lalu"
            
        # Menghasilkan hash_code yang stabil
        hash_object = hashlib.sha1()
        hash_object.update(title.encode('utf-8'))
        news_hash = hash_object.hexdigest()
        
        news_info = {
            "judul": title,
            "kategori": category,
            "waktu_publish": time_ago,
            "waktu_scraping": scrape_time.strftime("%H:%M:%S\n%A, %d %B %Y"),
            "hash_code": news_hash,
            "waktu_real_publish" : scrape_time.strftime("%H:%M:%S\n%A, %d %B %Y"),
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
        
        
        '''Jika waktu yang disediakan oleh aplikasi dalam bentuk tanggal(bukan .... menit yang lalu)'''
        # Ubah waktu publish agar update dengan waktu nyata (real-time)
        # for item in existing_data:
        #     publish_time_str = item["waktu_publish"].split('\n')
        #     if len(publish_time_str) == 2:
        #         publish_time = strptime_best(publish_time_str[1])
        #     else:
        #         publish_time = strptime_best(item["waktu_publish"])

        #     time_diff = datetime.datetime.now() - publish_time
        #     if time_diff.days > 0:
        #         time_ago = f"{time_diff.days} hari yang lalu"
        #     elif time_diff.seconds // 3600 > 0:
        #         time_ago = f"{time_diff.seconds // 3600} jam yang lalu"
        #     elif time_diff.seconds // 60 > 0:
        #         time_ago = f"{time_diff.seconds // 60} menit yang lalu"
        #     elif time_diff.seconds % 60 > 0:
        #         time_ago = f"{time_diff.seconds % 60} detik yang lalu"
        #     item["waktu_publish"] = f"{time_ago}\n{item['waktu_publish'].split('\n')[1]}"
        
        # Tambahkan data baru ke data yang sudah ada
        all_data = existing_data
        all_data.extend(new_data)
        
        # Mengurutkan data sebelum disimpan
        sorted_data = sorted(all_data, key=lambda x: x['waktu_real_publish'], reverse=True)

        # Simpan semua data ke file JSON
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(new_data)} new news items to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")


if __name__=="__main__":
    news_data = scrape_news()
    save_to_json(news_data)
