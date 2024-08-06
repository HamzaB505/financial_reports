import os
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time
import random
from urllib.parse import urljoin, urlparse
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from robotexclusionrulesparser import RobotExclusionRulesParser
from requests.exceptions import RequestException
from selenium.webdriver.common.by import By

# Set up logging
logging.basicConfig(filename='financial_report_downloader.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define the companies, their sectors, and the URLs of their financial reports
companies = [
    {"name": "Apple", "sector": "Technology", "url": "https://investor.apple.com/investor-relations/default.aspx"},
    {"name": "Microsoft", "sector": "Technology", "url": "https://www.microsoft.com/en-us/Investor/earnings/FY-2023/q4/"},
    {"name": "Johnson & Johnson", "sector": "Healthcare", "url": "https://www.investor.jnj.com/quarterly-results"},
    {"name": "JPMorgan Chase", "sector": "Finance", "url": "https://www.jpmorganchase.com/ir/quarterly-earnings"},
    {"name": "Walmart", "sector": "Retail", "url": "https://corporate.walmart.com/newsroom/financial-reports"},
    {"name": "Amazon", "sector": "Technology", "url": "https://ir.aboutamazon.com/quarterly-results/default.aspx"},
    {"name": "Berkshire Hathaway", "sector": "Finance", "url": "https://www.berkshirehathaway.com/reports.html"},
    {"name": "Tesla", "sector": "Automotive", "url": "https://ir.tesla.com/financial-information/quarterly-results"},
    {"name": "Alphabet", "sector": "Technology", "url": "https://abc.xyz/investor/"},
    {"name": "Meta", "sector": "Technology", "url": "https://investor.fb.com/financials/default.aspx"},
    {"name": "NVIDIA", "sector": "Technology", "url": "https://investor.nvidia.com/financial-info/financial-reports/default.aspx"},
    {"name": "Procter & Gamble", "sector": "Consumer Goods", "url": "https://www.pginvestor.com/financial-reporting/quarterly-results/default.aspx"},
    {"name": "Visa", "sector": "Finance", "url": "https://investor.visa.com/financial-information/quarterly-earnings/default.aspx"},
    {"name": "UnitedHealth", "sector": "Healthcare", "url": "https://www.unitedhealthgroup.com/investors/financial-reports-filings.html"},
    {"name": "ExxonMobil", "sector": "Energy", "url": "https://corporate.exxonmobil.com/investors/investor-relations"},
    {"name": "Pfizer", "sector": "Healthcare", "url": "https://investors.pfizer.com/Financials/Quarterly-Results/default.aspx"},
    {"name": "Coca-Cola", "sector": "Consumer Goods", "url": "https://investors.coca-colacompany.com/financial-information/quarterly-results"},
    {"name": "PepsiCo", "sector": "Consumer Goods", "url": "https://www.pepsico.com/investors/financial-information/quarterly-earnings"},
    {"name": "AbbVie", "sector": "Healthcare", "url": "https://investors.abbvie.com/events-and-presentations"}
]

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def is_allowed_by_robots(url):
    rp = RobotExclusionRulesParser()
    try:
        rp.fetch(urljoin(url, "/robots.txt"))
        return rp.is_allowed("*", url)
    except:
        logging.warning(f"Could not fetch robots.txt for {url}")
        return True

def download_pdf(url, folder_path, filename):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        filepath = os.path.join(folder_path, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(response.content)
            logging.info(f"Downloaded: {filename}")
        else:
            logging.info(f"File already exists: {filename}")
    except RequestException as e:
        logging.error(f"Failed to download {filename}: {str(e)}")

def extract_pdf_links_selenium(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)  # Allow time for any JavaScript to load
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf') or 'pdf' in href.lower():
                full_url = urljoin(url, href)
                pdf_links.append(full_url)
        return pdf_links
    except Exception as e:
        logging.error(f"Failed to extract PDF links from {url} using Selenium: {str(e)}")
        return []
    finally:
        driver.quit()

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def handle_specific_website(company):
    pdf_links = []
    
    if company['name'] == 'Apple':
        # Apple's investor relations page requires navigation to find PDFs
        driver = setup_selenium_driver()
        try:
            driver.get(company['url'])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "main")))
            
            # Navigate to the financial reports section
            financial_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Financial Information')]")
            financial_link.click()
            
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "report-list")))
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            pdf_links = [a['href'] for a in soup.select('.report-list a[href$=".pdf"]')]
        finally:
            driver.quit()

    elif company['name'] == 'Microsoft':
        # Microsoft's earnings page has direct PDF links
        response = requests.get(company['url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = [a['href'] for a in soup.select('a[href$=".pdf"]')]

    elif company['name'] == 'Amazon':
        # Amazon's IR page requires JavaScript rendering
        driver = setup_selenium_driver()
        try:
            driver.get(company['url'])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quarterly-result")))
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            pdf_links = [a['href'] for a in soup.select('.quarterly-result a[href$=".pdf"]')]
        finally:
            driver.quit()

    elif company['name'] == 'JPMorgan Chase':
        # JPMorgan's page has a specific structure for quarterly reports
        response = requests.get(company['url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = [a['href'] for a in soup.select('.quarterly-results a[href$=".pdf"]')]

    elif company['name'] == 'Berkshire Hathaway':
        # Berkshire Hathaway's page is simple HTML
        response = requests.get(company['url'])
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = [a['href'] for a in soup.select('a[href$=".pdf"]')]

    elif company['name'] == 'Tesla':
        # Tesla's IR page requires JavaScript rendering
        driver = setup_selenium_driver()
        try:
            driver.get(company['url'])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quarterly-results")))
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            pdf_links = [a['href'] for a in soup.select('.quarterly-results a[href$=".pdf"]')]
        finally:
            driver.quit()

    else:
        logging.warning(f"No specific handler for {company['name']}, using default method.")
        pdf_links = extract_pdf_links_selenium(company['url'])

    return pdf_links

def setup_selenium_driver():
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def extract_pdf_links_selenium(url):
    driver = setup_selenium_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)  # Allow time for any JavaScript to load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return [a['href'] for a in soup.select('a[href$=".pdf"]')]
    except Exception as e:
        logging.error(f"Failed to extract PDF links from {url} using Selenium: {str(e)}")
        return []
    finally:
        driver.quit()

def main():
    base_folder = f"financial_reports_{datetime.now().strftime('%Y_%m_%d')}"
    create_folder(base_folder)

    for company in companies:
        if not is_allowed_by_robots(company['url']):
            logging.warning(f"Skipping {company['name']} due to robots.txt restrictions")
            continue

        sector_folder = os.path.join(base_folder, company['sector'])
        create_folder(sector_folder)
        
        company_folder = os.path.join(sector_folder, company['name'])
        create_folder(company_folder)
        
        try:
            pdf_links = extract_pdf_links_selenium(company['url'])
            if not pdf_links:
                handle_specific_website(company)
                continue

            for link in pdf_links:
                parsed_url = urlparse(link)
                filename = os.path.basename(parsed_url.path)
                filename = sanitize_filename(filename)
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
                download_pdf(link, company_folder, filename)
                time.sleep(random.uniform(1, 3))  # Random delay between downloads
        except Exception as e:
            logging.error(f"Error processing {company['name']}: {str(e)}")

    logging.info("Completed downloading financial reports")

if __name__ == "__main__":
    main()