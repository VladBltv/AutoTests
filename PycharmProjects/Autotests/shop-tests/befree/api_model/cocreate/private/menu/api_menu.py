from .endpoints import Endpoints
from .payloads import Payloads
from befree.api_model.config.headers import Headers
from befree.api_model import api
from requests import Response


class Menu:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get(self):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_menu,
            headers=self._headers.common,
        )
        return response
