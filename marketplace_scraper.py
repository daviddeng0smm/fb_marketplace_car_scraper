import string
from typing import List
from selenium.webdriver.support.ui import Select
from numpy import double
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init_driver():
    logging.info("Initializing ChromeDriver")
    service = ChromeService(executable_path="C:\\Users\\David\\PycharmProjects\\chromedriver.exe")
    options = Options()
    options.headless = True  # Run in headless mode for faster execution
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def yearGrabber(entireTitle: str) -> int:
    logging.info("Extracting year from title")
    answer = entireTitle.split(' ')
    holder = answer[0]
    return int(holder)


def mileGrabber(entireTitle: str) -> double:
    logging.info("Extracting mileage from title")
    answer = entireTitle.split('K')
    holder = answer[0]
    holder = double(holder)
    holder *= 1000
    return holder


def brandGrabber(entireTitle: str) -> str:
    logging.info("Extracting brand from title")
    answer = entireTitle.split(' ')
    return answer[1]


def modelGrabber(entireTitle: str) -> str:
    logging.info("Extracting model from title")
    answer = entireTitle.split(' ')
    if len(answer) > 2:
        return answer[2]
    else:
        return "No Model Name"


def titleParser(titleList):
    logging.info("Parsing titles")
    finalParsedResult = []
    for title in titleList:
        title_details = title.split('\n')

        # searches for two prices
        if '$' in title_details[0] and '$' in title_details[1]:
            title_details.pop(1)

        if (len(title_details) == 5) and ("K" in title_details[3]):
            miles = mileGrabber(title_details[3])
            model = modelGrabber(title_details[1])
            brand = brandGrabber(title_details[1])
            year = yearGrabber(title_details[1])
            parsed_result = [
                title_details[0],  # price
                year,  # year
                brand,  # brand
                model,  # model
                title_details[2],  # location
                miles,  # mileage
                title_details[4]  # link
            ]
            finalParsedResult.append(parsed_result)
    return finalParsedResult


def excelWriter(parsedTitleList, filename='processed_titles.xlsx'):
    logging.info(f"Writing data to {filename}")
    df = pd.DataFrame(parsedTitleList, columns=['Price', 'Year', 'Make', 'Model', 'Location', 'Mileage', 'Link', 'VIN'])
    df.to_excel(filename, index=False)
    logging.info(f"Data has been written to {filename}")


def linkGrabber(htmlSegment):
    logging.info("Extracting link from HTML segment")
    splitSegment = htmlSegment.split('"')
    return "https://www.facebook.com" + splitSegment[3]


def facebookScraper(url="https://www.facebook.com/marketplace/la/vehicles?minPrice=3000&maxMileage=70000&minYear=2016"
                        "&topLevelVehicleType=car_truck&exact=false"):
    logging.info(f"Starting Facebook scraper with URL: {url}")
    driver = init_driver()

    start_time = time.time()
    driver.get(url)
    logging.info(f"URL opened in {time.time() - start_time:.2f} seconds")

    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    body_element = driver.find_element(By.TAG_NAME, 'body')
    old_height = driver.execute_script("return document.body.scrollHeight")
    attempts = 0
    max_attempts = 5  # Maximum attempts to scroll when no new data is found

    while attempts < max_attempts:
        body_element.send_keys(Keys.END)
        time.sleep(1)  # Allow time for page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == old_height:
            attempts += 1  # No new data loaded
        else:
            old_height = new_height
            attempts = 0  # Reset attempts counter if new data was loaded

    try:
        containers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='x3ct3a4']")))
        if not containers:
            logging.error("No containers found. Check the CSS selector.")
            driver.quit()
            return []

    except Exception as e:
        logging.error(f"Failed to find containers: {str(e)}")
        driver.quit()
        return []

    candidates = []
    for container in containers:
        link = linkGrabber(container.get_attribute("innerHTML"))
        candidates.append(container.text + "\n" + link)

    parsed_titles = titleParser(candidates)
    driver.quit()

    return parsed_titles


def extract_vin(driver):
    logging.info("Extracting VIN")
    vin_pattern = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')  # VIN pattern
    try:
        # First layout: basics-content-wrapper
        basics_wrapper = driver.find_element(By.CLASS_NAME, "basics-content-wrapper")
        dt_elements = basics_wrapper.find_elements(By.TAG_NAME, "dt")
        dd_elements = basics_wrapper.find_elements(By.TAG_NAME, "dd")

        for dt, dd in zip(dt_elements, dd_elements):
            if dt.text == "VIN":
                vin = dd.text.strip()
                if vin_pattern.match(vin):
                    return vin
    except NoSuchElementException:
        pass

    try:
        # Second layout: flex items-center
        flex_elements = driver.find_elements(By.CSS_SELECTOR, "div.flex.items-center")
        for flex_element in flex_elements:
            if "VIN:" in flex_element.text:
                vin = flex_element.text.split("VIN:")[1].strip()
                if vin_pattern.match(vin):
                    return vin
    except NoSuchElementException:
        pass

    return "False"


def gettingAutoTempest(parsedTitleList):
    logging.info("Starting AutoTempest search")
    driver = init_driver()
    indices_to_remove = []

    for i, listing in enumerate(parsedTitleList):
        price, year, make, model, location, mileage, link = listing

        logging.info(f"Searching AutoTempest for {year} {make} {model}")
        # Construct URL
        url = (
            f"https://www.autotempest.com/results?"
            f"make={make.lower()}&model={model.lower()}&zip=94579&radius=500"
            f"&minyear={year}&maxyear={year}&minmiles={int(mileage - 5000)}&maxmiles={int(mileage)}"
            f"&title=clean"
        )

        try:
            driver.get(url)
            driver.maximize_window()

            try:
                # Attempt to locate the dropdown element and select "Lowest Price"
                ddown = driver.find_element(By.ID, 'sort-secondary')
                select = Select(ddown)
                select.select_by_visible_text("Lowest Price")
            except NoSuchElementException:
                logging.error(f"Dropdown not found for listing: {listing}")
                indices_to_remove.append(i)
                continue

            time.sleep(3)

            try:
                # Locate all listings
                listings = driver.find_elements(By.CSS_SELECTOR, "li.result-list-item a.listing-link")
                for listing_index, listing_to_click in enumerate(listings):
                    try:
                        # Remove the target attribute to prevent opening in a new tab
                        driver.execute_script("arguments[0].removeAttribute('target');", listing_to_click)
                        # Click on the link
                        listing_to_click.click()

                        time.sleep(3)

                        # Extract VIN
                        vin = extract_vin(driver)
                        if vin == "False":
                            logging.info("VIN not found, marking for removal")
                            indices_to_remove.append(i)  # Collect index to remove
                        else:
                            logging.info(f"VIN found: {vin}")
                            parsedTitleList[i].append(vin)  # Append VIN to the listing
                            break

                    except (StaleElementReferenceException, ElementNotInteractableException):
                        logging.error(f"Element not interactable or stale for listing: {listing}")
                        indices_to_remove.append(i)
                        break  # Skip to the next listing

            except NoSuchElementException:
                logging.info("No more listings found.")
                break

        except WebDriverException as e:
            logging.error(f"WebDriver exception occurred: {str(e)}")
            indices_to_remove.append(i)

    logging.info(f"Indices to remove: {indices_to_remove}")
    logging.info(f"Length of parsedTitleList before removal: {len(parsedTitleList)}")

    # Remove collected indices in reverse order to avoid re-indexing issues
    for index in sorted(indices_to_remove, reverse=True):
        logging.info(f"Removing index: {index}")
        parsedTitleList.pop(index)

    logging.info(f"Length of parsedTitleList after removal: {len(parsedTitleList)}")

    driver.quit()
    for listing in parsedTitleList:
        print(listing)
        print('\n')
    return parsedTitleList


parsed_title = facebookScraper()
updated_parsed_title = gettingAutoTempest(parsed_title)
excelWriter(updated_parsed_title)
