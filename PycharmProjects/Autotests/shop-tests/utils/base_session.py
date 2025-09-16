from requests import Session
from utils.loging import request_logger


class BaseSession(Session):
    def __init__(self, **kwargs):
        self.base_url = kwargs.pop("base_url")

        if "api_key" in kwargs:
            self.api_key = kwargs.pop("api_key")
        else:
            self.api_key = ""

        if "type" in kwargs:
            self.type = kwargs.pop("type")
        else:
            self.type = ""

        super().__init__()

    @request_logger
    def request(self, method, url, **kwargs):
        headers = {}
        if "headers" in kwargs:
            headers = kwargs.pop("headers")

        if len(self.api_key) > 0:
            if self.type == "basic":
                headers["Authorization"] = f"Basic {self.api_key}"
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"

        return super().request(
            method, url=f"{self.base_url}{url}", headers=headers, **kwargs
        )
