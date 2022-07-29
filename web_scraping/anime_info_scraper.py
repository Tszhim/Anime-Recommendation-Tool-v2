import csv
import pickle
import time
from typing import List
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from web_scraping.scraper_utils import get_driver, navigate_to, remove_cookies_popup

# Define constants.
ANIME_DATA_F = "csv_output/anime_data.csv"
NUM_ANIME_SCRAPED_F = "csv_output/num_anime_scraped.txt"
TOTAL_NUM_ANIME = 12831

def get_num_anime_scraped() -> int:
    """
    Read from NUM_ANIME_SCRAPED_F to get number of already scraped anime.
    :return: number of already scraped anime.
    """
    path = Path(NUM_ANIME_SCRAPED_F)
    if path.is_file():
        with open(NUM_ANIME_SCRAPED_F, 'rb') as file:
            num_anime_scraped = pickle.load(file)
        return num_anime_scraped
    else:
        return 0


def save_num_anime_scraped(num_scraped: int) -> None:
    """
    Write to NUM_ANIME_SCRAPED_F to save number of already scraped anime.
    :param num_scraped: number of already scraped anime.
    :return: None
    """
    with open(NUM_ANIME_SCRAPED_F, 'wb') as file:
        pickle.dump(num_scraped, file)


def parse_anime_info(info: List[WebElement]) -> List[str]:
    """
    Parse all anime info from extracted webelements.
    :param info: list of webelements from anime webpage.
    :return: anime_info as a single string, delimited by ','.
    """
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
        if len(text) < 2:
            continue
        label, content = text[0], text[1]

        if label == "Type":
            show_type = content
        elif label == "Episodes":
            episodes = content
        elif label == "Aired":
            try:
                start_month = content[0:4]
                split_mt_yr = content.split(", ") if len(content.split(", ")) > 0 else content.split(" ")
                start_year = split_mt_yr[1]

                if start_month.startswith("Jan") or start_month.startswith("Feb"):
                    premiered = "Winter " + start_year[0:4]
                elif start_month.startswith("Mar") or start_month.startswith("Apr") or start_month.startswith("May"):
                    premiered = "Spring " + start_year[0:4]
                elif start_month.startswith("Jun") or start_month.startswith("Jul") or start_month.startswith("Aug"):
                    premiered = "Summer " + start_year[0:4]
                elif start_month.startswith("Sep") or start_month.startswith("Oct") or start_month.startswith("Nov"):
                    premiered = "Fall " + start_year[0:4]
                elif start_month.startswith("Dec"):
                    premiered = "Winter " + str(int(start_year[0:4]) + 1)
            except IndexError:
                continue
        elif label == "Studios":
            studios = content
        elif label == "Source":
            source = content
        elif label == "Genre" or label == "Genres":
            genres = content
        elif label == "Theme" or label == "Themes":
            theme = content
        elif label == "Rating":
            age_rating = content
        elif label == "Score":
            score = content.split(" ")[0]
        elif label == "Ranked":
            ranking = content.split("#")[1]
        elif label == "Popularity":
            popularity_rank = content.split("#")[1]

    # show_type,episodes,premiered,studios,source,genres,theme,age_rating,score,ranking,popularity_rank
    parsed_info = [show_type, episodes, premiered, studios, source, genres, theme, age_rating, score, ranking, popularity_rank]

    return parsed_info


def create_anime_data_file() -> None:
    """
    Creates ANIME_DATA_F if it does not exist and establishes relevant headers.
    :returns: None
    """
    path = Path(ANIME_DATA_F)
    if not path.is_file():
        with open(ANIME_DATA_F, 'w', encoding="utf-8", newline="") as file:
            # If csv file doesn't exist, create and add column labels.
            writer = csv.writer(file)
            writer.writerow(["title", "show_type", "episodes", "premiered", "studios", "source",
                             "genres", "theme", "age_rating", "score", "ranking", "popularity_rank"])


# Maintain a counter storing number of scraped animes.
NUM_ANIME_SCRAPED = get_num_anime_scraped()
create_anime_data_file()

# Setting up webdriver and opening webpage.
driver = get_driver()
navigate_to(driver, "https://myanimelist.net/topanime.php")
remove_cookies_popup(driver)

# Loop through each page of the "Top Anime" page.
for page in range(NUM_ANIME_SCRAPED, TOTAL_NUM_ANIME, 50):
    ranking_page = f"https://myanimelist.net/topanime.php?limit={NUM_ANIME_SCRAPED}"
    navigate_to(driver, ranking_page)
    time.sleep(2)

    anime_info_links = []
    element_list = driver.execute_script("return document.querySelectorAll(\".anime_ranking_h3\")")

    # Get links to each of the 50 anime on the current webpage and add it to a list.
    for element in element_list:
        anchor = element.find_element(By.TAG_NAME, "a")
        anime_info_links.append(anchor.get_attribute("href"))

    # Loop through each link and collect information about the anime, then append it to .csv file.
    for link in anime_info_links:
        navigate_to(driver, link)
        time.sleep(1)

        # Get the title of the anime (english if exists, then japanese).
        title_element = driver.execute_script("return document.querySelectorAll(\".h1-title\")")[0]

        try:
            title_name = title_element.find_element(By.CLASS_NAME, "title-english").text
        except NoSuchElementException:
            title_name = title_element.find_element(By.TAG_NAME, "strong").text

        # Get other details about the anime.
        leftside_info = driver.execute_script("return document.querySelectorAll(\".leftside .spaceit_pad\")")
        parsed_info = parse_anime_info(leftside_info)

        # Append info to csv file.
        csv_line = [title_name] + parsed_info
        print(csv_line)

        with open(ANIME_DATA_F, 'a', encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(csv_line)

        NUM_ANIME_SCRAPED += 1
        save_num_anime_scraped(NUM_ANIME_SCRAPED)

        # Sleep thread to avoid sending requests to MAL servers too fast.
        time.sleep(1)

driver.quit()
print("Finished collecting data")
