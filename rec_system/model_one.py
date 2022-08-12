import pandas as pd

from db.connection import get_db_connection
from db.query import get_full_merge

# Fetch full table from database
engine, conn, meta_data = get_db_connection()
full_table = get_full_merge(conn, meta_data)

# Set pandas options for printing
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', None)

# Convert table to DataFrame
full_table = pd.DataFrame(full_table)

# Create separate DataFrame containing only USERNAME, ANIME_TITLE, USER_RATING
user_item_table = full_table.filter(['USERNAME', 'SCORE', 'ANIME_TITLE'], axis=1)

# Create DataFrame where USERNAME is rows, ANIME_TITLE is columns, USER_RATING is entry [USERNAME, ANIME_TITLE]
user_item_table = user_item_table.pivot_table(index=['USERNAME'],
                                              columns='ANIME_TITLE',
                                              values='SCORE')
print(user_item_table.head())
