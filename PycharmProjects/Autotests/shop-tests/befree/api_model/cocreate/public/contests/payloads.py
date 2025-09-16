import json
from utils import helpers
from befree.api_model.cocreate import utils


class Payloads:
    def get_projects(self, **kwargs):
        payload = {}

        if "query" in kwargs:
            if kwargs["query"] is not None:
                payload["query"] = kwargs.pop("query")

        if "isVisibleOnMainPage" in kwargs:
            if kwargs["isVisibleOnMainPage"] is not None:
                payload["filter"] = {"isVisibleOnMainPage": kwargs.pop("isVisibleOnMainPage")}

        if "page" in kwargs:
            if kwargs["page"] is not None:
                payload["page"] = kwargs.pop("page")
        else:
            payload["page"] = 1

        if "perPage" in kwargs:
            if kwargs["perPage"] is not None:
                payload["perPage"] = kwargs.pop("perPage")
        else:
            payload["perPage"] = 10

        return json.dumps(payload)
