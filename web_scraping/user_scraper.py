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
from webdriver_manager.chrome import ChromeDriverManager

# Driver/file/time settings.
EXE_LOC = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
DRIV_VERS = '104.0.5112.20'
USER_DATA_F = "user_data.csv"
USERNAME_F = "usernames.csv"
DELAY_MIN = 10
DELAY_MAX = 15
POSTS_CT = 50
start = time.time()


# Returns a set of usernames that were already searched from USERNAME_F. If the file does not exist, create it and establish relevant headers.
def get_searched_users() -> Set[str]:
    collected_users = set()
    if path.exists(USERNAME_F):
        with open(USERNAME_F, 'r', encoding='UTF8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                collected_users.add(row[0])
            f.close()
    else:
        with open(USERNAME_F, 'x', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Username"])
            f.close()
    return collected_users


# Creates USER_DATA_F if it does not exist and establishes relevant headers.
def setup_user_data_file() -> None:
    if not path.exists(USER_DATA_F):
        with open(USER_DATA_F, 'x', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Username", "Anime_Title", "Score", "Watch_Progress", "Watch_Status"])
            f.close()


# Get an instance of Selenium webdriver with set configurations.
def get_driver() -> webdriver:
    opts = Options()
    # opts.headless = True
    opts.binary_location = EXE_LOC
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=DRIV_VERS).install()), options=opts)
    return driver


# Given an instance of a webdriver and a URL, navigate to the URL. If not successful, terminate the program.
def navigate_to(driver: webdriver, url: str) -> None:
    try:
        driver.get(url)
    except TimeoutException:
        driver.quit()
        sys.exit("Failed to load page. Terminating program.")


# Scrolls to the bottom of the current webpage.
def scroll_to_bottom(driver: webdriver) -> None:
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# Remove cookies popup on "https://myanimelist.net". If not successful, terminate the program.
def remove_cookies_popup(driver: webdriver) -> None:
    try:
        popup = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]")))
        driver.execute_script("arguments[0].click();", popup)
    except TimeoutException:
        driver.quit()
        sys.exit("Did not find popup.")


# Retrieve the number of forum posts specified by num. Returns the URLs as a list of strings.
def get_forum_posts(driver: webdriver, num: int) -> List[str]:
    posts = []
    for show in range(0, num, 50):
        navigate_to(driver, f"https://myanimelist.net/forum/?board=1&show={show}")
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        post_containers = driver.find_elements(By.CSS_SELECTOR, "td[class*='forum_boardrow1']:not([align='right'])")
        for post_container in post_containers:
            anchors = post_container.find_elements(By.CSS_SELECTOR, "a[href^='/forum']")
            for anchor in anchors:
                posts.append(anchor.get_attribute("href"))
    return posts


# Given a list of forum posts, return users' anime lists URLs as a set of strings.
def get_anime_lists(driver: webdriver, posts: List[str]) -> Set[str]:
    users = set()
    for post in posts:
        navigate_to(driver, post)
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        user_containers = driver.find_elements(By.CSS_SELECTOR, "a[href*='/profile']:not([class='forum-icon'])")
        for user_container in user_containers:
            if "myanimelist" in user_container.get_attribute("href"):
                users.add(user_container.get_attribute("href").replace("profile", "animelist"))
    return users


# Given a list of anime lists and a set of already searched users, store all new data into respective USER_DATA_F and OUTPUT_F files.
def store_user_data(driver: webdriver, anime_lists: Set[str], searched_users: Set[str]) -> None:
    for anime_list in anime_lists:
        navigate_to(driver, anime_list)
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        # If username already searched, skip.
        username = driver.current_url.split("/animelist/")[1]
        if username in searched_users:
            continue

        # Extract relevant anime data.
        try:
            # Open stats.
            stats_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[id='show-stats-button']")))
            driver.execute_script("arguments[0].click();", stats_button)
            stats = driver.find_element(By.CSS_SELECTOR, "div[class='list-stats']")
            days = stats.text.split(',')[5].split(": ")[1]

            # Skip user if watch time < 1 day.
            if float(days) > 1:
                # Load all of the entries by scrolling.
                scroll_to_bottom(driver)

                # Retrieve relevant element blocks.
                title_containers = driver.find_elements(By.CSS_SELECTOR,
                                                        "td[class='data title clearfix'] > a[class='link sort']")
                score_containers = driver.find_elements(By.CSS_SELECTOR, "span[class*='score-label']")
                progress_containers = driver.find_elements(By.CSS_SELECTOR, "td[class*='data progress']")
                status_containers = driver.find_elements(By.CSS_SELECTOR, "td[class*='data status']")

                # Write anime entry information (anime_title, score, watch_progress, watch_status) to file.
                skipped = False
                for title_ele, score_ele, progress_ele, status_ele in zip(title_containers, score_containers,
                                                                          progress_containers, status_containers):
                    title = title_ele.text
                    score = score_ele.text
                    progress = progress_ele.text
                    status = status_ele.get_attribute("class").split(' ')[2]

                    # Skip if any fields are empty.
                    if title and score and progress and status:
                        with open(USER_DATA_F, 'a', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([username, title, score, progress, status])
                            f.close()
                    else:
                        skipped = True

                # Print to console if skipped.
                if skipped:
                    print(f"Fields were undefined on {username}'s watchlist. Skipped.")
            else:
                print(f"{username}'s list did not meet the watchtime minimum.")

        # Print stack trace if page could not be scraped.
        except (IndexError, ValueError, NoSuchElementException, TimeoutException):
            print(username + "'s profile caused an exception:\n")
            traceback.print_exc()

        # Write username to skip on next encounter and add it to set.
        searched_users.add(username)
        with open('usernames.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username])
            f.close()

        # For metrics.
        print(get_lapsed_time())


# Returns the amount of time lapsed from the start of execution to present.
def get_lapsed_time() -> float:
    return time.time() - start


# Get list of usernames that were already searched.
s_users = get_searched_users()

# Setup user data collection file.
setup_user_data_file()

# Navigate to main page and remove cookies popup.
d = get_driver()
navigate_to(d, "https://myanimelist.net/")
remove_cookies_popup(d)

# Get POSTS_CT recent posts.
f_posts = get_forum_posts(d, POSTS_CT)

# Get users' anime lists from the posts.
a_lists = get_anime_lists(d, f_posts)

# Store user data.
store_user_data(d, a_lists, s_users)

# Close driver on completion.
d.quit()
