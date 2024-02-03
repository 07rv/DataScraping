from selenium import webdriver
from selenium.webdriver.common.by import By
from fuzzywuzzy import fuzz
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
browser = webdriver.Chrome()

class CompanyInfo:
    url = os.getenv('LINKEDIN_DOMAIN')
    threshold = float(os.getenv('THRESHOLD'))
    time_sleep = float(os.getenv('SLEEP_TIME_LOW'))

    def login(self, user_email, user_password):

        browser.get(self.url)

        username = browser.find_element(By.ID, 'session_key')
        username.send_keys(user_email)
        password = browser.find_element(By.ID, 'session_password')
        password.send_keys(user_password)
        login_btn = browser.find_element(By.CLASS_NAME, 'sign-in-form__submit-btn--full-width')
        login_btn.click()

    def convert_to_numeric(self, value):
        multiplier = 1
        if 'K' in value:
            multiplier = 1000
            value = value.replace('K', '')
        elif 'M' in value:
            multiplier = 1000000
            value = value.replace('M', '')

        return float(value) * multiplier
    
    def getcompanylink(self, company_name):
        url = f'{self.url}/search/results/companies/?keywords={company_name}'
        browser.get(url)
        time.sleep(self.time_sleep)

        try:
            companies = browser.find_elements(By.CLASS_NAME, 'entity-result__item')
            
            highest_followers_count = 0
            company_link = None
            for company in companies:
                name = company.find_element(By.CLASS_NAME, 'entity-result__title-text')
                name = name.find_element(By.TAG_NAME, 'a')
                link = name.get_attribute("href")
                follower = company.find_element(By.CLASS_NAME, 'entity-result__secondary-subtitle')
                follower = self.convert_to_numeric(follower.text.split(' ')[0])
              
                similarity_ratio = fuzz.ratio(name.text.lower(), company_name.lower())
                if similarity_ratio > self.threshold:
                    if follower > highest_followers_count:
                        highest_followers_count = follower
                        company_link = link

            return highest_followers_count, company_link

        except Exception as e:
            print(e)
            return '',''
        
    def getcompanydata(self, link):
        try: 
            url = f'{link}/people'
            browser.get(url)

            time.sleep(self.time_sleep)
            number = browser.find_element(By.XPATH, '//div[@class="org-people__header-spacing-carousel"]/h2[@class="text-heading-xlarge"]')

            return int(number.text.split()[0].replace(',', ''))
        except Exception as e: 
            return 0
    
    def getcompanyjobs(self, company):
        url = f'{self.url}/jobs/search/?keywords={company}'
        browser.get(url)
        time.sleep(self.time_sleep)

        filter = browser.find_element(By.ID, 'searchFilter_timePostedRange')
        filter.click()

        wait = WebDriverWait(browser, 10)
        options = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='hoverable-outlet-date-posted-filter-value']//ul/li/label")))
        options[3].click()
        time.sleep(self.time_sleep)

        show_result = filter.find_element(By.XPATH, "//div[@id='hoverable-outlet-date-posted-filter-value']//div[contains(@class, 'reusable-search-filters-buttons')]//button[2]")
        show_result.click()
        time.sleep(self.time_sleep)

        xpath = '//div[@class="jobs-search-results-list__subtitle"]/span'
        job = browser.find_element(By.XPATH, xpath)
        job = job.text
        time.sleep(self.time_sleep)

        return job.split()[0].replace(',','')
    
    def companyinfo(self):
        df_mcompany = pd.read_csv('Linkedin/Data/m_company.csv')
        companydata = {'Company': [],'Empolyee': [], 'Follower': [], 'Jobs': [], 'Date': []}
        today_date = datetime.today().date()
        file_name = 'Linkedin/Data/t_companyinfo.csv'

        for index, row in df_mcompany.iterrows():
            Company = row['Company']

            follower, link = self.getcompanylink(Company)

            if link != '':
                empolyee = self.getcompanydata(link)
                job = self.getcompanyjobs(Company)

            companydata['Company'].append(Company)
            companydata['Empolyee'].append(empolyee)
            companydata['Follower'].append(follower)
            companydata['Jobs'].append(job)
            companydata['Date'].append(today_date)

        df_company_data = pd.DataFrame(companydata)

        if os.path.exists(file_name):
            df_companies = pd.read_csv(file_name)
            df_company_data = pd.concat([df_company_data, df_companies],ignore_index=True)
            
        df_company_data.to_csv(file_name, index=False, encoding='utf-8')