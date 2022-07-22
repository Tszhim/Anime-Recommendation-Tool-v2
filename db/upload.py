from os import path
import csv
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Text, Float, select
from typing import Set

# Define file locations.
ANIME_DATA_F = "../web_scraping/csv_output/anime_data.csv"
USER_DATA_F = "../web_scraping/csv_output/user_data.csv"

def create_tables(engine, meta_data) -> None:
    """
    Create necessary tables to store scraped data.
    :param engine: engine object returned from connection.py
    :param meta_data: metadata object returned from connection.py
    :return: None
    """
    users = Table("users", meta_data,
                  Column("USER_ID", Integer, autoincrement=True, primary_key=True),
                  Column("USERNAME", String(255)))

    anime_data = Table("anime_data", meta_data,
                       Column("ANIME_ID", Integer, autoincrement=True, primary_key=True),
                       Column("ANIME_TITLE", String(255)),
                       Column("ANIME_SHOW_TYPE", String(10)),
                       Column("ANIME_EPISODES", Integer),
                       Column("ANIME_PREMIERED", String(15)),
                       Column("ANIME_SOURCE", Text),
                       Column("ANIME_STUDIOS", Text),
                       Column("ANIME_GENRES", Text),
                       Column("ANIME_THEMES", Text),
                       Column("ANIME_AGE_RATING", String(255)),
                       Column("ANIME_SCORE", Float(4)),
                       Column("ANIME_RANKING", Integer),
                       Column("ANIME_POPULARITY", Integer))

    user_data = Table("user_data", meta_data,
                      Column("USER_ID", Integer, ForeignKey('users.USER_ID')),
                      Column("ANIME_ID", Integer, ForeignKey('anime_data.ANIME_ID')),
                      Column("SCORE", Integer),
                      Column("CURR_EPISODE", Integer),
                      Column("WATCH_STATUS", String(9)))

    meta_data.create_all(engine)

def add_anime_data(connection, meta_data) -> None:
    """
    Push data from ANIME_DATA_F to relevant database table.
    :param connection: connection object returned from connection.py
    :param meta_data: metadata object returned from connection.py
    :return: None
    """
    anime_data_table = meta_data.tables["anime_data"]

    if path.exists(ANIME_DATA_F):
        with open(ANIME_DATA_F, 'r', encoding='UTF8') as f:
            reader = csv.reader(f)
            header = next(reader)

            # Scan through each row and parse/cast appropriately.
            for row in reader:
                entry = {"ANIME_TITLE": row[0], "ANIME_SHOW_TYPE": row[1], "ANIME_PREMIERED": row[3],
                         "ANIME_STUDIOS": row[4], "ANIME_SOURCE": row[5], "ANIME_GENRES": row[6],
                         "ANIME_THEMES": row[7], "ANIME_AGE_RATING": row[8], "ANIME_SCORE": float(row[9]),
                         "ANIME_RANKING": int(row[10]), "ANIME_POPULARITY": int(row[11])}

                if row[2] != "Unknown":
                    entry["ANIME_EPISODES"] = int(row[2])

                connection.execute(anime_data_table.insert(), entry)

            f.close()


def add_user_data(connection, meta_data) -> None:
    """
    Push data from USER_DATA_F to relevant database tables.
    :param connection: connection object returned from connection.py
    :param meta_data: metadata object returned from connection.py
    :return: None
    """

    users_table = meta_data.tables["users"]
    user_data_table = meta_data.tables["user_data"]
    anime_data_table = meta_data.tables["anime_data"]

    if path.exists(USER_DATA_F):
        with open(USER_DATA_F, 'r', encoding='UTF8') as f:
            reader = csv.reader(f)
            header = next(reader)
            v_users = valid_users()

            # Scan through each row and complete the following:
            # 1) Add user to users table if the username has not been encountered yet.
            # 2) Extract the user id.
            # 3) Find matching anime name from anime_data table, and extract the anime id.
            # 4) Push the relevant information into user_data table.

            for row in reader:
                # Steps 1 and 2:
                if row[0] not in v_users:
                    continue
                username = row[0]
                user_id_query = select(users_table.columns.USER_ID).where(users_table.columns.USERNAME == username)
                user_id_res = connection.execute(user_id_query).fetchone()
                user_id = None

                try:
                    user_id = user_id_res[0]
                except TypeError:
                    res = connection.execute(users_table.insert(), {"USERNAME": username})
                    user_id = res.lastrowid

                # Step 3:
                anime_title = row[1]
                anime_id_query = select(anime_data_table.columns.ANIME_ID).where(anime_data_table.columns.ANIME_TITLE == anime_title)
                anime_id_res = connection.execute(anime_id_query).fetchone()
                anime_id = anime_id_res[0]

                # Step 4:
                entry = {"USER_ID": user_id, "ANIME_ID": anime_id, "WATCH_STATUS": row[4]}

                if row[2] != "-":
                    entry["SCORE"] = int(float(row[2]))
                if row[3] != '-':
                    entry["WATCH_PROGRESS"] = row[3]

                connection.execute(user_data_table.insert(), entry)

            f.close()

def valid_users() -> Set[str]:
    """
    Return a list of users with valid watch data (must have at least 2 of the following: watching/completed/dropped/onhold)
    :return: a set containing usernames of users with valid data.
    """
    collected_users = set()
    with open(USER_DATA_F, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            collected_users.add(row[0])
        f.close()

    df = pd.read_csv("user_data.csv")
    for user in collected_users:
        user_df = df.loc[df["Username"] == user]
        watching = user_df.loc[user_df["Watch_Status"] == "watching"].shape[0]
        completed = user_df.loc[user_df["Watch_Status"] == "completed"].shape[0]
        dropped = user_df.loc[user_df["Watch_Status"] == "dropped"].shape[0]
        onhold = user_df.loc[user_df["Watch_Status"] == "onhold"].shape[0]

        statuses = 0
        if watching:
            statuses = statuses + 1
        if completed:
            statuses = statuses + 1
        if dropped:
            statuses = statuses + 1
        if onhold:
            statuses = statuses + 1

        if statuses < 2:
            collected_users.remove(user)

    return collected_users
