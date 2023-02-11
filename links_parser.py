import csv
import time
from multiprocessing.pool import ThreadPool
from threading import Thread

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class LinksParser:
    def __init__(self, links: list[str]) -> None:
        self.links: list[str] = links
        self.properties: list[dict] = []

    def run_parser(self) -> None:
        self.threaded_parser()
        self.export_to_csv()

    def export_to_csv(self) -> None:
        with open("output.csv", "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, self.properties[0].keys())
            writer.writeheader()
            writer.writerows(self.properties)

    def open_link(self, link: str) -> str:
        while True:
            try:
                return requests.get(link).text
            except:
                print("Connection Error, trying again")
                time.sleep(2)

    def parse_html(self, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        property_info = {
            "الاسم": soup.select_one("#collapse2 .col-xs-12:nth-child(1) .labelValue").get_text(strip=True),
            "المدينة": soup.select_one(
                "#collapse3 .col-xs-12:nth-child(2) .labelValue"
            ).get_text(strip=True),
            "المنطقة": soup.select_one(
                "#collapse3 .col-xs-12:nth-child(1) .labelValue"
            ).get_text(strip=True),
            "الحي": soup.select_one("#collapse3 .col-xs-12:nth-child(3) .labelValue").get_text(strip=True),
            "الشارع": soup.select_one("#collapse3 .col-xs-12:nth-child(4) .labelValue").get_text(strip=True),
            "صندوق البريد": soup.select_one(
                "#collapse3 .col-xs-12:nth-child(5) .labelValue"
            ).get_text(strip=True),
            "الرمز الريدي": soup.select_one(
                "#collapse3 .col-xs-12:nth-child(6) .labelValue"
            ).get_text(strip=True),
            "الجوال": soup.select_one(".col-md-6+ .labelValue").get_text(strip=True),
            "البريد الالكتروني": soup.select_one("#collapse4 .col-md-5+ .labelValue").get_text(strip=True),
        }

        return property_info

    def parse_link(self, link: str) -> dict:
        html = self.open_link(link)
        return self.parse_html(html)

    def threaded_parser(self) -> None:
        pool: ThreadPool = ThreadPool(40)

        with tqdm(total=len(self.links), desc="Getting Properties Info: ") as bar:
            for result in pool.imap_unordered(self.parse_link, self.links):
                self.properties.append(result)
                bar.update()