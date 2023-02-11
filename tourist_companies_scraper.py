import contextlib
import os
import time
import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome, ChromeOptions, find_chrome_executable
from win32api import HIWORD, GetFileVersionInfo

from captcha_solver import CaptchaSolver


def _chrome_main_version():
    filename = find_chrome_executable()
    info = GetFileVersionInfo(filename, "\\")
    return HIWORD(info["FileVersionMS"])


class TouristScraper(Chrome):
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            with contextlib.suppress(OSError):
                self.quit()
        except:
            pass

    def __init__(self):
        options = ChromeOptions()
        prefs = {"download.default_directory": os.getcwd()}
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        options.add_argument(
            "--User-Agent=='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'"
        )
        options.add_experimental_option("prefs", prefs)
        super().__init__(version_main=_chrome_main_version(), options=options)
        self.wait = 45
        self.properties_links = set()
        self.BASE_URL = "https://tlg.mt.gov.sa"
        self.captcha_solver = CaptchaSolver(self)

    def open_website(self) -> None:
        self.get("https://tlg.mt.gov.sa/IwaaFacilitiesSearch")

    def refresh_recaptcha(self) -> None:
        self.refresh()
        time.sleep(2)

    def initiate_search(self) -> None:
        captcha = "sound"
        while captcha.lower() == "sound" or len(str(captcha)) < 4:
            self.refresh()
            WebDriverWait(self, self.wait).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, "#frm_Search .rightTit"))
            ).click()
            captcha = self.captcha_solver.run_solver(
                WebDriverWait(self, 15)
                .until(ec.presence_of_element_located((By.CLASS_NAME, "BDC_SoundLink")))
                .get_attribute("href")
            )

            try:
                int(captcha)
            except:
                captcha = "sound"
            WebDriverWait(self, self.wait).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, "#CaptchaCode"))
            ).send_keys(captcha)

        time.sleep(5)

        WebDriverWait(self, self.wait).until(
            ec.visibility_of_element_located(
                (By.CSS_SELECTOR, "#select2-ddl_ActivityId-container")
            )
        ).click()

        time.sleep(0.5)

        self.find_element(
            By.CSS_SELECTOR, "#select2-ddl_ActivityId-results"
        ).find_elements(By.TAG_NAME, "li")[-1].click()

        self.find_element(By.CSS_SELECTOR, "#btn_Search").click()

    def wait_loading(self) -> None:
        WebDriverWait(self, self.wait).until(
            ec.invisibility_of_element_located((By.ID, "divOverlay"))
        )

    def page_properties_links(self) -> None:
        self.wait_loading()

        for link in WebDriverWait(self, self.wait).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr"))
        ):
            self.properties_links.add(
                urllib.parse.urljoin(
                    self.BASE_URL,
                    link.find_element(By.TAG_NAME, "a").get_attribute("href"),
                )
            )

    def move_to_next_page(self) -> bool:
        while True:
            try:
                next_page_btn = WebDriverWait(self, self.wait).until(
                    ec.element_to_be_clickable(
                        (By.CLASS_NAME, "jtable-page-number-next")
                    )
                )

                if "jtable-page-number-disabled" in next_page_btn.get_attribute(
                    "outerHTML"
                ):
                    return False
                next_page_btn.click()
                return True
            except:
                pass
