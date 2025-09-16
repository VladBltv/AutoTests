from befree.api_model.cocreate.public.main_page.endpoints import Endpoints
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class MainPage:
    def __init__(self):
        self._endpoints = Endpoints()
        self._headers = Headers()

    def get_main_page(self):
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_main_page,
            headers=self._headers.common,
        )
        return response
