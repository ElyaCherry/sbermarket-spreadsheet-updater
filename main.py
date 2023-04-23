from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
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

driver = webdriver.Firefox(options=options)  # create a new Firefox webdriver instance

end_sheet = client.open_by_key(spreadsheet_id).get_worksheet(1)
source_sheet = client.open_by_key(spreadsheet_id).worksheet('urls')


# Define a function to scrape prices from a URL
def scrape_price(cell, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 3.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        meta_element = soup.find("meta", {"data-qa": "meta-price"})
        price = meta_element.get("content").replace('.', ',')
    except Exception as e:
        print(f"Error scraping cell {cell.row} {cell.col}, URL {url}: {e}")
        print("html:")
        print(soup)
        print("retrying...")
        try:
            driver.get(url)
            # time.sleep(6)
            WebDriverWait(driver, 9)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            meta_element = soup.find("meta", {"data-qa": "meta-price"})
            price = meta_element.get("content").replace('.', ',')
        except AttributeError:
            print("unsuccessful, skipped; please check cell", cell.row, cell.col, "manually")
            price = ""
        else:
            print("success!")
        # price = ""
    end_sheet.update_cell(cell.row, cell.col, price)


# Use a ThreadPoolExecutor to run multiple requests in parallel
executor = ThreadPoolExecutor(max_workers=2)  # 20
cell_range = source_sheet.range('D4:Q100')
for cell in cell_range:
    url = cell.value

    if not url:
        continue

    # Scrape the price in a separate thread
    executor.submit(scrape_price, cell, url)

# Wait for all tasks to complete
executor.shutdown(wait=True)

# for cell in cell_range:
#     url = cell.value
#     if url == '':
#         continue
#         # price = ""
#     else:
#         driver.get(url)
#
#         WebDriverWait(driver, 3)
#
#         print(cell.row, cell.col)
#
#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#
#         # Find the meta-price element and extract the price
#         try:
#             meta_element = soup.find("meta", {"data-qa": "meta-price"})
#             price = meta_element.get("content").replace('.', ',')
#             # print(price)
#         except AttributeError as e:
#             print("meta element or its content not found for cell", cell.row, cell.col)
#             print("at url:", url)
#             print("html:")
#             print(soup)
#             print("retrying...")
#             try:
#                 driver.get(url)
#                 # time.sleep(6)
#                 WebDriverWait(driver, 9)
#                 soup = BeautifulSoup(driver.page_source, 'html.parser')
#                 meta_element = soup.find("meta", {"data-qa": "meta-price"})
#                 price = meta_element.get("content").replace('.', ',')
#             except AttributeError:
#                 print("unsuccessful, skipped; please check cell", cell.row, cell.col, "manually")
#                 price = ""
#             else:
#                 print("success!")
#
#     end_sheet.update_cell(cell.row, cell.col, price)  # Write the price to the Google Spreadsheet

driver.quit()
