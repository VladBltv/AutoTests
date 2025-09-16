from befree.api_model.cocreate.private.collaborations.endpoints import Endpoints
from befree.api_model.cocreate.private.collaborations.payloads import Payloads
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class Collaborations:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get_list(self, query="", visibility="", page=1, per_page=10, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_collaborations,
            data=self._payloads.get_collaborations(query=query, visibility=visibility, page=page, per_page=per_page, **kwargs),
            headers=self._headers.common,
        )
        return response

    def delete(self, collaboration_id: str):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.delete_collaboration(collaboration_id=collaboration_id),
            headers=self._headers.common,
        )
        return response

    def get_one(self, collaboration_id: str):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_collaboration(collaboration_id=collaboration_id),
            headers=self._headers.common,
        )
        return response

    def update(self, collaboration_id: str, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.update_collaboration(collaboration_id=collaboration_id),
            data=self._payloads.update_collaboration(**kwargs),
            files=self._payloads.files(**kwargs),
        )
        return response

    def create(self, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.create_collaboration,
            data=self._payloads.create_collaboration(**kwargs),
            files=self._payloads.files(**kwargs),
        )
        return response

    def get_options(self):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_options,
            headers=self._headers.common,
        )
        return response
