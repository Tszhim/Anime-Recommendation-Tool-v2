import sys
import time
import random

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Driver/file/time settings.
EXE_LOC = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
DRIV_VERS = '104.0.5112.20'
START = time.time()

def get_driver() -> webdriver:
    """
    Get an instance of Selenium webdriver with set configurations.
    :return: webdriver.
    """
    opts = Options()
    # opts.headless = True
    opts.binary_location = EXE_LOC
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=DRIV_VERS).install()), options=opts)
    return driver

def navigate_to(driver: webdriver, url: str) -> None:
    """
    Navigate to specified URL on browser.
    :param driver: selenium webdriver instance.
    :param url: URL string to navigate to.
    :return: None
    """
    try:
        driver.get(url)
    except TimeoutException:
        driver.quit()
        sys.exit("Failed to load page. Terminating program.")

def scroll_to_bottom(driver: webdriver) -> None:
    """
    Scrolls to the bottom of the current webpage.
    :param driver: selenium webdriver instance.
    :return: None
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(10, 15))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def remove_cookies_popup(driver: webdriver) -> None:
    """
    Remove cookies popup on "https://myanimelist.net". If not successful, terminate the program.
    :param driver: selenium webdriver instance.
    :return: None
    """
    try:
        popup = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]")))
        driver.execute_script("arguments[0].click();", popup)
    except TimeoutException:
        driver.quit()
        sys.exit("Did not find popup.")

def get_lapsed_time() -> float:
    """
    Compute the amount of time lapsed from the start of execution to present.
    :return: the lapsed time.
    """
    return time.time() - START
