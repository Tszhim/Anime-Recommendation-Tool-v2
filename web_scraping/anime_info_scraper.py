import csv
import sys
import traceback
import time
import random
from os import path
from typing import List, Set
import pickle
from pathlib import Path

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

DRIV_VER = "103.0.5060.53"
TOTAL_NUM_ANIME = 12806
ANIME_DATA_F = "anime_data.csv"
NUM_ANIME_SCRAPED_F = "num_anime_scraped.txt"


def get_num_anime_scraped() -> int:
    path = Path(NUM_ANIME_SCRAPED_F)
    if path.is_file():
        with open(NUM_ANIME_SCRAPED_F, 'rb') as file:
            num_anime_scraped = pickle.load(file)
        return num_anime_scraped
    else:
        return 0


def save_num_anime_scraped(num_scraped: int) -> None:
    with open(NUM_ANIME_SCRAPED_F, 'wb') as file:
        pickle.dump(num_scraped, file)


def navigate_to(driver: webdriver, url: str) -> None:
    try:
        driver.get(url)
    except TimeoutException:
        driver.quit()
        sys.exit("Failed to load page. Terminating program.")


def remove_cookies_popup(driver: webdriver) -> None:
    try:
        popup = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]")))
        driver.execute_script("arguments[0].click();", popup)
    except TimeoutException:
        driver.quit()
        sys.exit("Did not find popup.")


def parse_anime_info(info: List[WebElement]) -> str:
    show_type = ""
    episodes = ""
    premiered = ""
    studios = ""
    source = ""
    genres = ""
    theme = ""
    age_rating = ""
    score = ""
    ranking = ""
    popularity_rank = ""

    for element in info:
        text = element.text
        if len(text) == 0:
            continue

        text = text.split(": ")
        label, content = text[0], text[1]

        if label == "Type":
            show_type = content
        elif label == "Episodes":
            episodes = content
        elif label == "Premiered":
            premiered = content
        elif label == "Studios":
            studios = "\"" + content + "\""
        elif label == "Source":
            source = content
        elif label == "Genres":
            genres = "\"" + content + "\""
        elif label == "Themes":
            theme = "\"" + content + "\""
        elif label == "Rating":
            age_rating = content
        elif label == "Score":
            score = content.split(" ")[0]
        elif label == "Ranked":
            ranking = content.split("#")[1]
        elif label == "Popularity":
            popularity_rank = content.split("#")[1]

    # show_type,episodes,premiered,studios,source,genres,theme,age_rating,score,ranking,popularity_rank
    parsed_info = show_type + "," + episodes + "," + premiered + "," + studios + "," + source + "," \
                  + genres + "," + theme + "," + age_rating + "," + score + "," + ranking + "," + popularity_rank

    return parsed_info


def append_anime_to_csv(csv_line: str):
    path = Path(ANIME_DATA_F)
    if not path.is_file():
        with open(ANIME_DATA_F, 'w', encoding="utf-8") as file:
            # If csv file doesn't exist, create and add column labels
            column_labels = "title,show_type,episodes,premiered,studios,source," \
                            "genres,theme,age_rating,score,ranking,popularity_rank\n"
            file.write(column_labels)

    # Append anime info to csv
    with open(ANIME_DATA_F, 'a', encoding="utf-8") as file:
        file.write(csv_line)
        file.write("\n")


NUM_ANIME_SCRAPED = get_num_anime_scraped()

# Setting up webdriver and opening webpage
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=DRIV_VER).install()))
navigate_to(driver, "https://myanimelist.net/topanime.php")
remove_cookies_popup(driver)

for page in range(NUM_ANIME_SCRAPED, TOTAL_NUM_ANIME, 50):
    ranking_page = f"https://myanimelist.net/topanime.php?limit={NUM_ANIME_SCRAPED}"
    navigate_to(driver, ranking_page)
    time.sleep(2)

    anime_info_links = []
    element_list = driver.execute_script("return document.querySelectorAll(\".anime_ranking_h3\")")

    # Get links to each anime on the current webpage and add it to a list
    for element in element_list:
        anchor = element.find_element(By.TAG_NAME, "a")
        anime_info_links.append(anchor.get_attribute("href"))

    # Loop through each link and collect information about the anime, then append it to .csv file
    for link in anime_info_links:
        navigate_to(driver, link)
        time.sleep(2)

        # Get the title of the anime
        title_element = driver.execute_script("return document.querySelectorAll(\".title-name\")")[0]
        title_name = title_element.find_element(By.TAG_NAME, "strong").text
        title_name = "\"" + title_name + "\""

        # Get other details about the anime
        leftside_info = driver.execute_script("return document.querySelectorAll(\".leftside .spaceit_pad\")")
        parsed_info = parse_anime_info(leftside_info)

        # Append info to csv file
        csv_line = title_name + "," + parsed_info
        print(csv_line)
        append_anime_to_csv(csv_line)

        NUM_ANIME_SCRAPED += 1
        save_num_anime_scraped(NUM_ANIME_SCRAPED)

        # Sleep thread to avoid sending requests to MAL servers too fast
        time.sleep(5)


print("Finished collecting data")
