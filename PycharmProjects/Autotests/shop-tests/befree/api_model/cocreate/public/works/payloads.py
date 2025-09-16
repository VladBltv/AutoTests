import json

from mimesis import Text

from utils import helpers
from befree.api_model.cocreate import utils
from befree.api_model.cocreate.public.works.schemas import update_work_request_schema


class Payloads:
    def get_works(self, **kwargs):
        payload = {}
        if "query" in kwargs:
            if kwargs["query"] is not None:
                payload["query"] = kwargs.pop("query")

        if "userId" in kwargs:
            if kwargs["userId"] is not None:
                payload["filter"] = {"userId": kwargs.pop("userId")}

        if "contestSlug" in kwargs:
            if kwargs["contestSlug"] is not None:
                if "filter" in payload:
                    payload["filter"]["contestSlug"] = kwargs.pop("contestSlug")

        if "bestWorks" in kwargs:
            if kwargs["bestWorks"] is not None:
                if "filter" in payload:
                    payload["filter"]["bestWorks"] = kwargs.pop("bestWorks")

        if "showMain" in kwargs:
            if kwargs["showMain"] is not None:
                if "filter" in payload:
                    payload["filter"]["showMain"] = kwargs.pop("showMain")

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

    def create_work(self, **kwargs):
        data = {}
        tags = {}

        if "title" in kwargs:
            if kwargs["title"] is not None:
                data["title"] = kwargs.pop("title")
        else:
            data["title"] = Text("ru").sentence()[:50]

        if "description" in kwargs:
            if kwargs["description"] is not None:
                data["description"] = kwargs.pop("description")
        else:
            data["description"] = Text("ru").sentence()[:500]

        if "contestId" in kwargs:
            if kwargs["contestId"] is not None:
                data["contestId"] = kwargs.pop("contestId")

        if "tags" in kwargs:
            if kwargs["tags"] is not None:
                tags = kwargs.pop("tags")
        else:
            tags = utils.set_work_tags()

        payload = {**data, **tags}

        return payload

    def update_work(self, current_data, **kwargs):
        schema = update_work_request_schema
        payload = helpers.get_payload_for_update(current_data=current_data, schema=schema, **kwargs)

        current_tags = current_data["tags"]
        if "tags" in kwargs:
            if kwargs["tags"] is not None:
                for i in range(len(kwargs["tags"])):
                    payload[f"tags[{i}]"] = kwargs["tags"][i]
        else:
            for i in range(len(current_tags)):
                payload[f"tags[{i}]"] = current_tags[i]

        if "images" in kwargs:
            if kwargs["images"] is not None:
                for i in range(len(kwargs["images"])):
                    payload[f"images[{i}]"] = kwargs["images"][i]

        return payload

    def files(self, **kwargs):
        if "images" in kwargs:
            if kwargs["images"] is not None:
                images = kwargs.pop("images")
        else:
            images = utils.set_work_images()

        if "cover" in kwargs:
            if kwargs["cover"] is not None:
                cover = kwargs.pop("cover")
        else:
            cover = utils.set_work_cover()

        files = {**images, **cover}

        return files
