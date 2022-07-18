import csv
import sys
import traceback
import time
import random
from os import path
from typing import List, Set

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

EXE_LOC = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
TOTAL_NUM_ANIME = 12806


def remove_cookies_popup(driver: webdriver) -> None:
    try:
        popup = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]")))
        driver.execute_script("arguments[0].click();", popup)
    except TimeoutException:
        driver.quit()
        sys.exit("Did not find popup.")


def parse_anime_info(info: List[WebElement]) -> str:
    show_type = None
    episodes = None
    premiered = None
    studios = None
    source = None
    genres = None
    theme = None
    age_rating = None
    score = None
    ranking = None
    popularity_rank = None

    for element in info:
        text = element.text
        if len(text) == 0:
            continue

        text = text.split(": ")
        label, content = text[0], text[1]

        if label == "Type":
            show_type = content
        elif label == "Episodes":
            episodes = int(content)
        elif label == "Premiered":
            premiered = content
        elif label == "Studios":
            studios = content
        elif label == "Source":
            source = content
        elif label == "Genres":
            genres = content
        elif label == "Themes":
            theme = content
        elif label == "Rating":
            age_rating = content
        elif label == "Score":
            score = content
        elif label == "Ranked":
            ranking = content
        elif label == "Popularity":
            popularity_rank = content

    return "hello world"


# Setting up webdriver and opening webpage
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("https://myanimelist.net/topanime.php")
remove_cookies_popup(driver)

element_list = driver.execute_script("return document.querySelectorAll(\".anime_ranking_h3\")")
anime_info_links = []

# Get links to each anime on the current webpage and add it to a list
for element in element_list:
    anchor = element.find_element(By.TAG_NAME, "a")
    anime_info_links.append(anchor.get_attribute("href"))

driver.get(anime_info_links[0])

leftside_info = driver.execute_script("return document.querySelectorAll(\".leftside .spaceit_pad\")")

parse_anime_info(leftside_info)



# Keep webpage open for debugging purposes
time.sleep(1000)
