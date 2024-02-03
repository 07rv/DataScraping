from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from dotenv import load_dotenv

from sectors import Sector

load_dotenv()
browser = webdriver.Chrome()

class Company:
    time_sleep = float(os.getenv('SLEEP_TIME_LOW'))

    def __init__(self):
        pass

    def get_companies(self, sectors):
        company = {'Sector': [],'Company': []}
        
        for index, row in sectors.iterrows():
            try:
                sector = row['Sector']
                link = row['Link']
                browser.get(link)
                time.sleep(self.time_sleep)

                pages_text = browser.find_element(By.CLASS_NAME, 'card-large')
                pages_text = pages_text.find_element(By.CLASS_NAME, 'flex-space-between')
                pages_text = pages_text.find_element(By.CLASS_NAME, 'sub')
                page = pages_text.text
                page = page.split()[-1]
                time.sleep(self.time_sleep)

                current_url = browser.current_url

                if page != "" or page is not None:
                    for i in range(1,int(page)+1):
                        url = current_url + '?page=' +str(i)
                        browser.get(url)
                        wait = WebDriverWait(browser, 10)
                        companies_name = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//table/tbody/tr/td[2]/a')))
                        for company_name in companies_name:
                            text = company_name.text
                            company['Sector'].append(sector)
                            company['Company'].append(text)
            except Exception as e:
                print(sectors)

        df_company = pd.DataFrame(company)
        df_company.to_csv('Linkedin/Data/m_company.csv', index=False, encoding='utf-8')

    def company(self):
        try:
            sector = Sector()
            df_sector = sector.getSectors()
            self.get_companies(df_sector)
        except Exception as ex:
            print(ex)


