from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
browser = webdriver.Chrome()

class Sector:
    url = os.getenv('SCREENER_DOMAIN')
    time_sleep = float(os.getenv('SLEEP_TIME_LOW'))

    def __init__(self):
        pass

    def getSectors(self):
        browser.get(self.url)
        time.sleep(self.time_sleep)

        companies = browser.find_element(By.CLASS_NAME, 'card-small')
        companies = companies.find_element(By.CLASS_NAME, 'flex-gap-12')
        time.sleep(self.time_sleep)

        a_tags = WebDriverWait(companies, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )

        sectors = {'Sector': [],'Link': []}
        for a_tag in a_tags:
            href = a_tag.get_attribute("href")
            text = a_tag.text
            sectors['Sector'].append(text)
            sectors['Link'].append(href)

        df_sectors = pd.DataFrame(sectors)
        df_sectors.to_csv('Linkedin/Data/m_sectors.csv', index=False, encoding='utf-8')

        browser.quit()
        return df_sectors
        