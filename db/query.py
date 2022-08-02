from sqlalchemy import select
from typing import List, Tuple

def get_all_users(connection, meta_data) -> List[Tuple[str, str]]:
    """
    Retrieves all entries from users table.
    :param connection: connection object returned from connection.py
    :param meta_data: metadata object returned from connection.py
    :return: tuple format: (USER_ID, USERNAME)
    """

    users_table = meta_data.tables["users"]
    query = users_table.select()
    res = connection.execute(query)
    return res.fetchall()

def get_all_anime_data(connection, meta_data) -> List[Tuple[str, ...]]:
    """
    Retrieves all entries from anime_data table.
    :param connection: connection object returned from connection.py
    :param meta_data: metadata object returned from connection.py
    :return: tuple format: (ANIME_ID, ANIME_TITLE, ANIME_SHOW_TYPE, ANIME_EPISODES, ANIME_PREMIERED, ANIME_SOURCE,
                            ANIME_STUDIOS, ANIME_GENRES, ANIME_THEMES, ANIME_AGE_RATING, ANIME_SCORE, ANIME_RANKING, ANIME_POPULARITY)
    """
    anime_data_table = meta_data.tables["anime_data"]
    query = anime_data_table.select()
    res = connection.execute(query)
    return res.fetchall()

def get_all_user_data(connection, meta_data) -> List[Tuple[str, ...]]:
    """
    Retrieves all entries from user_data table.
    :param connection: connection object returned from connection.py
    :param meta_data: metadata object returned from connection.py
    :return: tuple format: (USER_ID, ANIME_ID, SCORE, CURR_EPISODE, WATCH_STATUS)
    """
    user_data_table = meta_data.tables["user_data"]
    query = user_data_table.select()
    res = connection.execute(query)
    return res.fetchall()

def get_full_merge(connection, meta_data) -> List[Tuple[str, ...]]:
    """
    Merges all tables into one cohesive list without distracting columns.
    :param connection: connection object returned from connection.py
    :param meta_data: metadata object returned from connection.py
    :return: tuple format: (USERNAME, SCORE, CURR_EPISODE, WATCH_STATUS, ANIME_TITLE, ANIME_SHOW_TYPE, ANIME_EPISODES,
                            ANIME_PREMIERED, ANIME_SOURCE, ANIME_STUDIOS, ANIME_GENRES, ANIME_THEMES, ANIME_AGE_RATING,
                            ANIME_SCORE, ANIME_RANKING, ANIME_POPULARITY)
    """
    users_table = meta_data.tables["users"]
    anime_data_table = meta_data.tables["anime_data"]
    user_data_table = meta_data.tables["user_data"]

    joined = user_data_table.join(anime_data_table, user_data_table.columns.ANIME_ID == anime_data_table.columns.ANIME_ID)\
                            .join(users_table, user_data_table.columns.USER_ID == users_table.columns.USER_ID)

    query = select(users_table.columns.USERNAME,
                   user_data_table.columns.SCORE,
                   user_data_table.columns.CURR_EPISODE,
                   user_data_table.columns.WATCH_STATUS,
                   anime_data_table.columns.ANIME_TITLE,
                   anime_data_table.columns.ANIME_SHOW_TYPE,
                   anime_data_table.columns.ANIME_EPISODES,
                   anime_data_table.columns.ANIME_PREMIERED,
                   anime_data_table.columns.ANIME_SOURCE,
                   anime_data_table.columns.ANIME_STUDIOS,
                   anime_data_table.columns.ANIME_GENRES,
                   anime_data_table.columns.ANIME_THEMES,
                   anime_data_table.columns.ANIME_AGE_RATING,
                   anime_data_table.columns.ANIME_SCORE,
                   anime_data_table.columns.ANIME_RANKING,
                   anime_data_table.columns.ANIME_POPULARITY).select_from(joined)

    res = connection.execute(query)
    return res.fetchall()