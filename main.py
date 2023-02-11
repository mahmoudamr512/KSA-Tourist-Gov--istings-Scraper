from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from links_parser import LinksParser
from tourist_companies_scraper import TouristScraper


def get_all_links():
    with TouristScraper() as tourist:
        tourist.open_website()
        tourist.initiate_search()

        tourist.page_properties_links()
        all_pages = tourist.find_elements(By.CLASS_NAME, "jtable-page-number")[
            -1
        ].text.strip()
        print(f"Scraped links of page 1 out of {all_pages}\r")

        page_number = 2
        while tourist.move_to_next_page():
            tourist.page_properties_links()
            page_number = int(
                WebDriverWait(tourist, 15)
                .until(
                    ec.presence_of_element_located(
                        (By.CSS_SELECTOR, ".jtable-page-number-active")
                    )
                )
                .text
            )
            print(f"Scraped links of page {page_number} out of {all_pages}\r")

        print(f"Finished scraping, found {len(tourist.properties_links)} properties")

        with open("links.txt", "w") as f:
            for line in tourist.properties_links:
                f.write(f"{line}\n")
        tourist.quit()
        return list(tourist.properties_links)


def main() -> None:
    props_links = get_all_links()
    links_parser = LinksParser(links=props_links)
    links_parser.run_parser()


if __name__ == "__main__":
    main()
