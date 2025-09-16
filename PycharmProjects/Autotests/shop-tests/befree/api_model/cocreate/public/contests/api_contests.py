from .endpoints import Endpoints
from .payloads import Payloads
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class Contests:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get_one(self, contest_id, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_contest(contest_id=contest_id),
            headers={**self._headers.common, **token},
        )

        return response

    def projects(self, *kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_projects,
            data=self._payloads.get_projects(**kwargs),
            headers={**self._headers.common, **token},
        )

        return response
