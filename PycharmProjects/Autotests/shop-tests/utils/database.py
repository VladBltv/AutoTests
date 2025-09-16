import json

import psycopg2, pandas
from dotenv import load_dotenv
from utils.loging import sql_logger
from befree.api_model import db_connection

load_dotenv()


class DB:
    def __init__(self, credentials, **kwargs):
        self.database = credentials["database"]
        self.user = credentials["user"]
        self.password = credentials["password"]
        self.host = credentials["host"]
        self.port = credentials["port"]

    @sql_logger
    def get_data(self, query, **kwargs):
        conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        d = pandas.read_sql_query(query, conn)
        conn.close()
        request_data = pandas.DataFrame(d).to_dict("records")

        request_data = (
            str(request_data)
            .replace("Timestamp", "")
            .replace("(", "")
            .replace(")", "")
            .replace("'", '"')
            .replace("None", "null")
            .replace("True", "true")
            .replace("False", "false")
        )
        request_data = json.loads(request_data)

        return str(request_data)

    @sql_logger
    def insert_data(self, query, data, **kwargs):
        conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

        cursor = conn.cursor()
        cursor.executemany(query, data)
        conn.commit()
        cursor.close()

    @sql_logger
    def update_data(self, query, **kwargs):
        conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()


def forming_request_update(data):
    params_list = data["field_name"]
    params_list[:] = [f" {el} = %s" for el in params_list]
    params_string = ", ".join(params_list)

    query = (
            f'update {data["table"]}'
            + "\nset "
            + params_string
            + f'\nwhere {data["record_identifier"]} = %s'
    )
    return query


def filling_out_table(data, service):
    query = forming_request_update(data)

    if service == "catalog":
        db_connection.catalog.insert_data(query, data["data"])
    if service == "cocreate":
        db_connection.cocreate.insert_data(query, data["data"])
