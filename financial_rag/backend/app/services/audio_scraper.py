import requests
from bs4 import BeautifulSoup
import os
import re

def download_mp3(url, folder_path, filename):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        filepath = os.path.join(folder_path, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"File already exists: {filename}")
    except requests.RequestException as e:
        print(f"Failed to download {filename}: {str(e)}")

def scrape_and_download_mp3s():
    url = "https://investors.coca-colacompany.com/filings-reports/resource-center"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    mp3_links = soup.find_all('a', href=re.compile(r'\.mp3$'))
    
    folder_path = os.path.join("data/audio", "coca_cola_earnings_audio")
    os.makedirs(folder_path, exist_ok=True)
    
    for link in mp3_links:
        mp3_url = link['href']
        filename = mp3_url.split('/')[-1]
        download_mp3(mp3_url, folder_path, filename)

if __name__ == "__main__":
    scrape_and_download_mp3s()