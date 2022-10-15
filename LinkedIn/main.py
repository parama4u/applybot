# This is a sample Python script.
import time
import  configparser,os
import pandas as pd

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



from selenium import webdriver as wd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import  By
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager



# Press the green button in the gutter to run the script.

class LINKEDIN(object):
    def __init__(self):
        self.HOME = "https://www.linkedin.com/uas/login"
        self.driver = wd.Chrome(ChromeDriverManager().install(),
                                options=self.browser_options())
        self.set_configs()

    def set_configs(self):
        cfg = configparser.ConfigParser()
        cfg.read('LinkedIn/config.ini')
        self.user_name = cfg.get('LOGIN','USERNAME')
        self.password = cfg.get('LOGIN','PASSWORD')

    def browser_options(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")

        # Disable webdriver flags or you will be easily detectable
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-blink-features=automated test software")
        return options

    def apply(self):
        self.open()
        self.search()

    def open(self):
        self.driver.get(self.HOME)
        time.sleep(2)
        self.login()

    def login(self):
        user_field = self.driver.find_element("id", "username")
        pw_field = self.driver.find_element("id", "password")
        login_button = self.driver.find_element("xpath",
                                                 '//*[@id="organic-div"]/form/div[3]/button')
        user_field.send_keys(self.user_name)
        pw_field.send_keys(self.password)
        time.sleep(2)
        login_button.click()
        time.sleep(2)

    def search(self):
        self.driver.get('https://www.linkedin.com/jobs/')
        data = pd.read_csv('LinkedIn/search.csv'
                           )
        # txt_keyword = self.driver.find_element("id","jobs-search-box-keyword-id-ember25")
        # txt_location = self.driver.find_element("id","jobs-search-box-location-id-ember25")
        for index,record in data.iterrows():
            txt_keyword = self.driver.find_element(By.XPATH, "//*[contains(@id,'jobs-search-box-keyword-id')]")
            txt_keyword.clear()
            txt_keyword.send_keys(record['keyword'])
            txt_keyword.send_keys(Keys.ENTER)
            time.sleep(10)
            txt_location = self.driver.find_element(By.XPATH, "//*[contains(@id,'jobs-search-box-location-id')]")
            txt_location.clear()
            print(record['location'])
            txt_location.send_keys(record['location'])
            txt_location.send_keys(Keys.RETURN)
            time.sleep(10)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
