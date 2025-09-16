import allure
from allure_commons.types import AttachmentType
from curlify import to_curl
import json
from json import JSONDecodeError


def add_screenshot(browser):
    png = browser.driver.get_screenshot_as_png()
    allure.attach(
        body=png,
        name="screenshot",
        attachment_type=AttachmentType.PNG,
        extension=".png",
    )


def add_logs(browser):
    log = "".join(f"{text}\n" for text in browser.driver.get_log(log_type="browser"))
    allure.attach(
        body=log,
        name="browser_logs",
        attachment_type=AttachmentType.TEXT,
        extension=".log",
    )


def add_html(browser):
    html = browser.driver.page_source
    allure.attach(
        body=html,
        name="page_source",
        attachment_type=AttachmentType.HTML,
        extension=".html",
    )


def add_video(browser):
    video_url = "https://selenoid.befree.ru/video/" + browser.driver.session_id + ".mp4"
    html = (
        "<html><body><video width='100%' height='100%' controls autoplay><source src='"
        + video_url
        + "' type='video/mp4'></video></body></html>"
    )
    allure.attach(
        body=html,
        name="video_" + browser.driver.session_id,
        attachment_type=AttachmentType.HTML,
        extension=".html",
    )


def add_api_request(response):
    if response.request.body:
        body = response.request.body
        if isinstance(body, bytes):
            response.request.body = bytes(
                str(response.request.body).replace("\\x", ""), encoding="utf-8"
            )
    allure.attach(
        body=to_curl(response.request).encode("utf-8"),
        name=f"Request {response.status_code}",
        attachment_type=AttachmentType.TEXT,
        extension=".txt",
    )


def add_api_response_json(response):
    allure.attach(
        body=json.dumps(response.json(), indent=4).encode("utf8"),
        name=f"Response {response.status_code}",
        attachment_type=AttachmentType.JSON,
        extension=".json",
    )


def add_api_response_txt(response):
    allure.attach(
        body=response.text,
        name=f"Response {response.status_code}",
        attachment_type=AttachmentType.TEXT,
        extension=".txt",
    )


def add_sql_query(query):
    allure.attach(
        body=query,
        name="Database query",
        attachment_type=AttachmentType.TEXT,
        extension=".txt",
    )


def add_sql_data(data):
    allure.attach(
        body=data,
        name="Database data",
        attachment_type=AttachmentType.JSON,
        extension=".json",
    )
