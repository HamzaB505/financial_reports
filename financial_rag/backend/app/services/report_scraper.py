import os
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Set up logging
logging.basicConfig(filename='financial_report_downloader.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

DOWNLOAD_DIR = "data"

def setup_selenium_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# Update all instances where webdriver.Chrome is called to use this function

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
    except requests.RequestException as e:
        logging.error(f"Failed to download {filename}: {str(e)}")

def handle_specific_website(company):
    pdf_links = []
    try:
        print(company['name'])
        if company['name'] == 'Berkshire Hathaway':
            # Berkshire Hathaway's page is simple HTML, but we need to construct the URLs
            base_url = "https://www.berkshirehathaway.com/"
            company_name = company['name'].lower().replace(' ', '')
            current_year = datetime.now().year
            for year in range(current_year + 1, 2010, -1):
                for quarter in range(1, 4):
                    year_short = str(year)[-2:]
                    if quarter == 1:
                        tmp = "1st"
                    elif quarter == 2:
                        tmp = "2nd"
                    elif quarter == 3:
                        tmp = "3rd"

                    url = f"{base_url}qtrly/{tmp}qtr{year_short}.pdf"
                    pdf_links.append(url)
                    
                url = f"{base_url}{year}ar/{year}ar.pdf"
                pdf_links.append(url)
                url = f"{base_url}letters/{year}ltr.pdf"
                pdf_links.append(url)


        elif company['name'] == 'Apple':
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
            except WebDriverException as e:
                logging.error(f"WebDriver error for {company['name']}: {str(e)}")
            finally:
                driver.quit()

        elif company['name'] == 'Amazon':
        # Amazon's IR page requires JavaScript rendering
            driver = setup_selenium_driver()
            try:
                driver.get(company['url'])
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "quarterly-result")))
            
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                pdf_links = [a['href'] for a in soup.select('.quarterly-result a[href$=".pdf"]')]
            except WebDriverException as e:
                logging.error(f"WebDriver error for {company['name']}: {str(e)}")
            finally:
                driver.quit()

        elif company['name'] == 'JPMorgan Chase':
            # JPMorgan's page has a specific structure for quarterly reports
            response = requests.get(company['url'])
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = [a['href'] for a in soup.select('.quarterly-results a[href$=".pdf"]')]


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
    except Exception as e:
        logging.error(f"Error handling {company['name']}: {str(e)}")
    
    return pdf_links

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
    # Define the companies, their sectors, and the URLs of their financial reports
    companies = [
        {"name": "Apple", "sector": "Technology", "url": "https://investor.apple.com/sec-filings/default.aspx"},
        {"name": "Microsoft", "sector": "Technology", "url": "https://www.microsoft.com/en-us/Investor/annual-reports.aspx"},
        {"name": "Johnson & Johnson", "sector": "Healthcare", "url": "https://www.investor.jnj.com/financials/quarterly-results/default.aspx"},
        {"name": "JPMorgan Chase", "sector": "Finance", "url": "https://www.jpmorganchase.com/ir/quarterly-earnings"},
        {"name": "Walmart", "sector": "Retail", "url": "https://stock.walmart.com/financials/quarterly-results/default.aspx"},
        {"name": "Amazon", "sector": "Technology", "url": "https://ir.aboutamazon.com/quarterly-results/default.aspx"},
        {"name": "Berkshire Hathaway", "sector": "Finance", "url": "https://www.berkshirehathaway.com/reports.html"},
        {"name": "Tesla", "sector": "Automotive", "url": "https://ir.tesla.com/#quarterly-disclosure"},
        {"name": "Alphabet", "sector": "Technology", "url": "https://abc.xyz/investor/"},
        {"name": "Meta", "sector": "Technology", "url": "https://investor.fb.com/financials/default.aspx"},
        {"name": "NVIDIA", "sector": "Technology", "url": "https://investor.nvidia.com/financial-info/financial-reports/default.aspx"},
        {"name": "Procter & Gamble", "sector": "Consumer Goods", "url": "https://www.pginvestor.com/financial-reporting/quarterly-results/default.aspx"},
        {"name": "Visa", "sector": "Finance", "url": "https://investor.visa.com/financial-information/quarterly-earnings/default.aspx"},
        {"name": "UnitedHealth", "sector": "Healthcare", "url": "https://www.unitedhealthgroup.com/investors/financial-reports.html"},
        {"name": "ExxonMobil", "sector": "Energy", "url": "https://corporate.exxonmobil.com/investors/investor-relations"},
        {"name": "Pfizer", "sector": "Healthcare", "url": "https://investors.pfizer.com/Investors/Financials/Quarterly-Results/"},
        {"name": "Coca-Cola", "sector": "Consumer Goods", "url": "https://investors.coca-colacompany.com/filings-reports/resource-center"},
        {"name": "PepsiCo", "sector": "Consumer Goods", "url": "https://investors.pepsico.com/investors/financial-information/quarterly-earnings/index.html"},
        {"name": "AbbVie", "sector": "Healthcare", "url": "https://investors.abbvie.com/annual-report-proxy"}
    ]
    base_folder = os.path.join(DOWNLOAD_DIR, f"financial_reports_{datetime.now().strftime('%Y_%m_%d')}")
    os.makedirs(base_folder, exist_ok=True)

    for company in companies:
        sector_folder = os.path.join(base_folder, company['sector'])
        os.makedirs(sector_folder, exist_ok=True)
        
        company_folder = os.path.join(sector_folder, company['name'])
        os.makedirs(company_folder, exist_ok=True)
        
        pdf_links = handle_specific_website(company)
        
        for link in pdf_links:
            filename = os.path.basename(link)
            download_pdf(link, company_folder, filename)
            time.sleep(random.uniform(1, 3))  # Random delay between downloads

    logging.info("Completed downloading financial reports")

if __name__ == "__main__":
    main()