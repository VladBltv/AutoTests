from .endpoints import Endpoints
from befree.api_model.config.headers import Headers
from befree.api_model import api
from requests import Response


class Options:
    def __init__(self):
        self._endpoints = Endpoints()
        self._headers = Headers()

    def get(self):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_options,
            headers=self._headers.common,
        )
        return response
