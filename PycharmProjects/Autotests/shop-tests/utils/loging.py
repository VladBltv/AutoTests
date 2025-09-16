from json import JSONDecodeError
import allure
from requests import Response
from utils import attachments
import json


def request_logger(function):
    def wrapper(*args, **kwargs):
        method, url = args[1], args[2]
        with allure.step(f"{method} {url}"):
            response: Response = function(*args, **kwargs)
            attachments.add_api_request(response)
            try:
                attachments.add_api_response_json(response)
            except JSONDecodeError:
                attachments.add_api_response_txt(response)
        return response

    return wrapper


def sql_logger(function):
    def wrapper(*args, **kwargs):
        query = args[1]
        with allure.step("SQL запрос"):
            attachments.add_sql_query(query)
            data = function(*args, **kwargs)
            data = (
                str(data)
                .replace("Timestamp", "")
                .replace("(", "")
                .replace(")", "")
                .replace("'", '"')
                .replace("None", "null")
                .replace("True", "true")
                .replace("False", "false")
            )
            data = json.loads(data)
            attachments.add_sql_data(json.dumps(data, indent=4))
        return data

    return wrapper
