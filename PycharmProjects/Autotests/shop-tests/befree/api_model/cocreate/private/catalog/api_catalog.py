from befree.api_model.cocreate.private.catalog.endpoints import Endpoints
from befree.api_model.cocreate.private.catalog.payloads import Payloads
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class Catalog:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get_list(self, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_compilations,
            data=self._payloads.get_compilations(**kwargs),
            headers=self._headers.common,
        )
        return response
