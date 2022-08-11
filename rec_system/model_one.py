import pandas as pd

from db.connection import get_db_connection
from db.query import get_full_merge

# Fetch full table from database
engine, conn, meta_data = get_db_connection()
full_table = get_full_merge(conn, meta_data)

# Set pandas options for printing
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Convert table to DataFrame
full_table = pd.DataFrame(full_table)



print(full_table.head())
