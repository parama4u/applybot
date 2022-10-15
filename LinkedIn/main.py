# This is a sample Python script.
import time

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



from selenium import webdriver as wd
from webdriver_manager.chrome import ChromeDriverManager

import LinkedIn.main

HOME = "https://www.linkedin.com/jobs/"
driver = wd.Chrome(ChromeDriverManager().install())

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    LinkedIn.main.LINKEDIN().apply()


class LINKEDIN(object):
    def __init__(self):
        pass

    def apply(self):

        driver.quit()

    def open(self):
        driver.get(HOME)
        time.sleep(5)

    def login(self):
        pass

    def search(self):
        pass

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
