import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, MetaData

def get_db_connection():
    """
    Establish database connection and return relevant objects for interaction.
    :return: an engine, connection, and meta_data object used for database communication.
    """
    load_dotenv(find_dotenv())
    engine = create_engine('mysql+mysqlconnector://{user}:{password}@{server}:{port}/{database}?charset=utf8'.format(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        server=os.getenv("SERVER"),
        port=os.getenv("PORT"),
        database=os.getenv("DATABASE")))
    connection = engine.connect()

    meta_data = MetaData(bind=engine)
    MetaData.reflect(meta_data)

    return engine, connection, meta_data
