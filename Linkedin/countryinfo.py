from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()
browser = webdriver.Chrome()

class CountryInfo:
    time_sleep = float(os.getenv('SLEEP_TIME_LOW'))
    url = os.getenv('LINKEDIN_DOMAIN')
    user_name = os.getenv('USER_NAME')
    password = os.getenv('USER_PASSWORD')

    def finddatacountry(self, country):
        url = f'{self.url}/jobs/search/?location={country}'
     
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
         
    def login(self, user_email, user_password):
        browser.get(self.url)
        username = browser.find_element(By.ID, 'session_key')
        username.send_keys(user_email)
        password = browser.find_element(By.ID, 'session_password')
        password.send_keys(user_password)
        login_btn = browser.find_element(By.CLASS_NAME, 'sign-in-form__submit-btn--full-width')
        login_btn.click()

    def countryinfo(self):

        self.login(self.user_name, self.password)
        
        today_date = datetime.today().date()
        file_name = 'Linkedin/Data/t_countryinfo.csv'
        
        country_list = pd.read_csv('Linkedin/Data/m_country.csv')
        lst  = country_list['Country']
        job_list_df = {'Country': [],'JobsCount': [], "Date": []}
        for item in lst:
            job = self.finddatacountry(item)
            job_list_df['Country'].append(item)
            job_list_df['JobsCount'].append(job)
            job_list_df['Date'].append(today_date)

        df = pd.DataFrame(job_list_df)
        if os.path.exists(file_name):
            job_list_df = pd.read_csv(file_name)
            df = pd.concat([df, job_list_df],ignore_index=True)            

        df.to_csv(file_name, index=False, encoding='utf-8')