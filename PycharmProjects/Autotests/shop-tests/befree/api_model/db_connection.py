import os

from dotenv import load_dotenv
from utils.database import DB

load_dotenv()

credentials_catalog = {
    "database": os.getenv("CATALOG_DATABASE_NAME"),
    "user": os.getenv("CATALOG_DATABASE_USER"),
    "password": os.getenv("CATALOG_DATABASE_PASSWORD"),
    "host": os.getenv("CATALOG_DATABASE_HOST"),
    "port": os.getenv("CATALOG_DATABASE_PORT"),
}
credentials_orders = {
    "database": os.getenv("ORDERS_DATABASE_NAME"),
    "user": os.getenv("ORDERS_DATABASE_USER"),
    "password": os.getenv("ORDERS_DATABASE_PASSWORD"),
    "host": os.getenv("ORDERS_DATABASE_HOST"),
    "port": os.getenv("ORDERS_DATABASE_PORT"),
}
credentials_monolith = {
    "database": os.getenv("MONOLITH_DATABASE_NAME"),
    "user": os.getenv("MONOLITH_DATABASE_USER"),
    "password": os.getenv("MONOLITH_DATABASE_PASSWORD"),
    "host": os.getenv("MONOLITH_DATABASE_HOST"),
    "port": os.getenv("MONOLITH_DATABASE_PORT"),
}
credentials_cocreate = {
    "database": os.getenv("COCREATE_DATABASE_NAME"),
    "user": os.getenv("COCREATE_DATABASE_USER"),
    "password": os.getenv("COCREATE_DATABASE_PASSWORD"),
    "host": os.getenv("COCREATE_DATABASE_HOST"),
    "port": os.getenv("COCREATE_DATABASE_PORT"),
}
credentials_config = {
    "database": os.getenv("CONFIG_DATABASE_NAME"),
    "user": os.getenv("CONFIG_DATABASE_USER"),
    "password": os.getenv("CONFIG_DATABASE_PASSWORD"),
    "host": os.getenv("CONFIG_DATABASE_HOST"),
    "port": os.getenv("CONFIG_DATABASE_PORT"),
}

catalog = DB(credentials=credentials_catalog)
orders = DB(credentials=credentials_orders)
monolith = DB(credentials=credentials_monolith)
cocreate = DB(credentials=credentials_cocreate)
config = DB(credentials=credentials_config)
