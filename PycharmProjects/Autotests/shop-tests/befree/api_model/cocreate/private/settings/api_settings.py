from .endpoints import Endpoints
from .payloads import Payloads
from befree.api_model.config.headers import Headers
from befree.api_model import api
from requests import Response


class Settings:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get(self):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_settings,
            headers=self._headers.common,
        )
        return response

    def update(self, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.update_settings,
            data=self._payloads.update_settings(**kwargs),
            headers=self._headers.common,
        )
        return response
