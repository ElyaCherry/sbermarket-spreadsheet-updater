from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions as exceptions
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import threading


load_dotenv()
credentials_path = os.getenv('CREDENTIALS_PATH')
spreadsheet_id = os.getenv('SPREADSHEET_ID')

scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

# set up Firefox options
options = Options()
options.add_argument('-headless')

source_sheet = client.open_by_key(spreadsheet_id).worksheet('urls')
end_sheet = client.open_by_key(spreadsheet_id).get_worksheet(0)

lock = threading.Lock()
tl = threading.local()


def scrape_price(cell, soup):
    meta_element = soup.find("meta", {"data-qa": "meta-price"})
    price = meta_element.get("content").replace('.', ',')
    # lock.acquire()
    # print("LOCKED for cell", cell.row, cell.col)
    end_sheet.update_cell(cell.row, cell.col, price)
    print(cell.row, cell.col, "success")
    # lock.release()
    # print("UNLOCKED for cell", cell.row, cell.col)


# Define a function to scrape prices from a URL
def get_url_write_price(cell, url):
    print(cell.row, cell.col)
    driver = webdriver.Firefox(options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 3.5).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                         'meta[data-qa="meta-price"]')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(cell.row, cell.col, "soup parsed")
        scrape_price(cell, soup)
    except exceptions as e:
        print(f"Error scraping cell {cell.row} {cell.col}, URL {url}: , html: ")
        print(f"retrying for cell {cell.row} {cell.col}...")
        try:
            driver.get(url)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                            'meta[data-qa="meta-price"]')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            scrape_price(cell, soup)
        except AttributeError:
            print(f"unsuccessful, skipped; please check cell {cell.row} {cell.col} manually")
            # tl.price = ""
        else:
            print("success!")
    finally:
        driver.quit()


executor = ThreadPoolExecutor(max_workers=10)  # 20 ?
cell_range = source_sheet.range('D4:Q100')
for cell in cell_range:
    url = cell.value

    if not url:
        continue

    executor.submit(get_url_write_price, cell, url)

executor.shutdown(wait=True)
