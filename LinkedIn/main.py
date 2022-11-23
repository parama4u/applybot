# This is a sample Python script.
import random
import time
import configparser, re
import selenium.common.exceptions
import csv
import pandas as pd
import logging, os
from datetime import datetime

from selenium import webdriver as wd
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

log = logging.getLogger(__name__)


class LINKEDIN(object):
    def __init__(self):
        self.HOME = "https://www.linkedin.com/uas/login"
        self.JOB = "https://www.linkedin.com/jobs/view/"
        self.driver = wd.Chrome(
            ChromeDriverManager().install(), options=self.browser_options()
        )
        self.set_configs()

    def set_configs(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read("./LinkedIn/config.ini")
        self.user_name = self.cfg.get("LOGIN", "USERNAME")
        self.password = self.cfg.get("LOGIN", "PASSWORD")
        self.phone = self.cfg.get("LOGIN", "PHONE")
        self.jobs_per_page = 25
        self.apply_button = None
        self.setup_logger()

    def setup_logger(self) -> None:
        dt: str = datetime.strftime(datetime.now(), "%m_%d_%y %H_%M_%S ")

        if not os.path.isdir("./logs"):
            os.mkdir("./logs")

        # TODO need to check if there is a log dir available or not
        logging.basicConfig(
            filename=("./logs/linkedin" + str(dt) + ".log"),
            filemode="w",
            format="%(asctime)s::%(name)s::%(levelname)s::%(message)s",
            datefmt="./logs/%d-%b-%y %H:%M:%S",
        )
        log.setLevel(logging.DEBUG)
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.DEBUG)
        c_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", "%H:%M:%S"
        )
        c_handler.setFormatter(c_format)
        log.addHandler(c_handler)

    def browser_options(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        # Disable webdriver flags or you will be easily detectable
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-blink-features=automated test software")
        return options

    def apply(self):
        self.open()
        self.login()
        self.search_apply()

    def open(self):
        self.driver.get(self.HOME)
        time.sleep(random.randint(1, 3))

    def login(self):
        user_field = self.driver.find_element("id", "username")
        pw_field = self.driver.find_element("id", "password")
        login_button = self.driver.find_element(
            "xpath", '//*[@id="organic-div"]/form/div[3]/button'
        )
        user_field.send_keys(self.user_name)
        pw_field.send_keys(self.password)
        time.sleep(random.randint(1, 3))
        login_button.click()
        time.sleep(random.randint(1, 3))

    def search_apply(self):
        data = pd.read_csv("./LinkedIn/search.csv")
        for index, record in data.iterrows():
            self.path = f"https://www.linkedin.com/jobs/search/?f_AL=true&f_TPR=r86400&keywords={record['keyword'].upper()}&location={record['location']}"
            self.driver.get(self.path)
            time.sleep(random.randint(1, 3))
            self.job_ids = []
            try:
                self.pages = self.driver.find_elements(
                    "xpath", "//li[@data-test-pagination-page-btn]"
                )[-1].get_attribute("data-test-pagination-page-btn")
            except IndexError:
                self.pages = 1
            self.get_jobs()
            self.iter_apply()
            for i in range(1, int(self.pages)):
                self.driver.get(f"{self.path}&start={(i)*self.jobs_per_page}")
                time.sleep(random.randint(1, 3))
                self.get_jobs()
                self.iter_apply()

    def get_jobs(self):
        self.job_ids = []
        for i in range(0, 20):
            self.driver.execute_script(f"window.scrollTo(0,{200*i})")
            time.sleep(random.randint(0, 2))
        self.jobs = self.driver.find_elements("xpath", "//li[@data-occludable-job-id]")
        for job in self.jobs:
            self.job_ids.append(job.get_attribute("data-occludable-job-id"))

    def ignore_jobs(self) -> bool:
        res = False
        time.sleep(random.randint(0, 3))
        self.ignore_keys = self.cfg.get("IGNORE", "desc").split(",")

        txt = {
            "title": self.driver.find_element(
                By.XPATH, "//*[contains(@class, 'jobs-unified-top-card')]"
            ).text.lower(),
            "description": self.driver.find_element(
                By.TAG_NAME, "article"
            ).text.lower(),
        }

        for key in self.ignore_keys:
            for content in txt.keys():
                if re.search(key.lower(), txt[content], re.I):
                    log.info(
                        f"Skip application to {self.driver.current_url}, found {key} in {content}"
                    )
        return res

    def application_fields(self, bt_name, bt_by, bt_value):
        try:
            self.res_elelements = self.driver.find_elements(bt_by, bt_value)
            return self.res_elelements[0]
        except (exceptions.NoSuchElementException, IndexError):
            log.info(f"{bt_name} not found.")
            return None

    def click_next(self, model_name):
        nav = self.application_fields(
            f"{model_name}: Next",
            By.CSS_SELECTOR,
            "button[aria-label='Continue to next step']",
        )
        if nav:
            nav.click()
        else:
            nav = self.application_fields(
                f"{model_name}: Review",
                By.CSS_SELECTOR,
                "button[aria-label='Review your application']",
            )
            if nav:
                nav.click()

    def easy_apply(self):
        time.sleep(random.randint(3, 5))
        apply_button = self.application_fields(
            "Easy apply", By.XPATH, "//*[contains(@class, 'jobs-apply-button')]"
        )
        if apply_button:
            apply_button.click()
            phone_number = self.application_fields(
                "Phone Number", By.XPATH, "//input[contains(@name,'phoneNumber')]"
            )

            if phone_number:
                phone_number.clear()
                phone_number.send_keys(self.phone)

            for next_ in ("Contact Info", "Resume"):
                self.click_next(next_)

            self.addtional_questions()

            for next_ in "Review":
                self.click_next(next_)

            try:
                submit_button = self.application_fields(
                    "Submit", By.CSS_SELECTOR, "button[aria-label='Submit application']"
                )
            except selenium.common.exceptions.NoSuchElementException:
                submit_button = self.application_fields(
                    "Submit", By.CSS_SELECTOR, "button[aria-label='Submit application']"
                )

            if submit_button:
                submit_button.click()
                log.info(f"Application Submitted {self.driver.current_url}")
                time.sleep(random.randint(1, 3))
        else:
            log.info(f"Skipping {self.driver.current_url}, Apply button not found")

    def addtional_questions(self):
        self.click_next("Additional Questions")
        self.application_fields(
            "Filed with errors", By.CSS_SELECTOR, "div[aria-invalid='true']"
        )
        for error in self.res_elelements:
            self.ans_queston(error)

    def get_answer(self, question):
        with open("./LinkedIn/additional_questions.csv", "r") as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                if row["question"].lower() in question.lower():
                    return row["answer"]

    def ans_queston(self, error):
        question = error.text.replace("\nRequired\nPlease enter a valid answer", "")
        question_type = "unknown"
        try:
            question_type = error.find_elements(By.TAG_NAME, "div")[0].get_attribute(
                "class"
            )
            if question_type == "fb-dropdown":
                from selenium.webdriver.support.ui import Select

                question = (
                    error.find_elements(By.TAG_NAME, "div")[0]
                    .find_elements(By.TAG_NAME, "select")[0]
                    .accessible_name.replace("* Required", "")
                )
                answer = self.get_answer(question)
                Select(
                    error.find_elements(By.TAG_NAME, "div")[0].find_elements(
                        By.TAG_NAME, "select"
                    )[0]
                ).select_by_visible_text(answer)
            elif question_type == "fb-single-line-text":
                answer = self.get_answer(question)
                error.find_elements(By.TAG_NAME, "div")[0].find_elements(
                    By.TAG_NAME, "input"
                )[0].send_keys(answer)

            elif question_type == "fb-multi-line-text":
                answer = self.get_answer(question)
                error.find_elements(By.TAG_NAME, "div")[0].find_elements(
                    By.TAG_NAME, "textarea"
                )[0].send_keys(answer)

            else:
                log.info(question_type)

        except IndexError:
            log.info(
                f"No Answer found for :  {question} : {question_type}. Skipping  {self.driver.current_url}"
            )
        except Exception as e:
            log.info(
                f"Exception {e} while answering {question} : {question_type} . Skipping  {self.driver.current_url}"
            )

    def iter_apply(self):
        for job_id in self.job_ids:
            job_page = f"{self.JOB}{job_id}"
            self.current_page = self.driver.get(job_page)
            if not self.ignore_jobs():
                log.info(f"Applying for {job_page}")
                self.easy_apply()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
