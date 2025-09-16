from befree.api_model.cocreate.private.contests.endpoints import Endpoints
from befree.api_model.cocreate.private.contests.payloads import Payloads
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class Contests:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get_list(self, query="", visibility="", page=1, per_page=10, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_contests,
            data=self._payloads.get_contests(query=query, visibility=visibility, page=page, per_page=per_page, **kwargs),
            headers=self._headers.common,
        )
        return response

    def delete(self, contest_id: str):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.delete_contest(contest_id=contest_id),
            headers=self._headers.common,
        )
        return response

    def get_one(self, contest_id: str):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_contest(contest_id=contest_id),
            headers=self._headers.common,
        )
        return response

    def update(self, contest_id: str, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.update_contest(contest_id=contest_id),
            data=self._payloads.update_contest(**kwargs),
            files=self._payloads.files(**kwargs),
        )
        return response

    def create(self, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.create_contest,
            data=self._payloads.create_contest(**kwargs),
            files=self._payloads.files(**kwargs),
        )
        return response
