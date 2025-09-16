import json, random
from mimesis import Text, Internet
from befree.api_model.cocreate import utils
from befree.api_model.cocreate.enums import CollabType


class Payloads:
    def get_collaborations(self, query, visibility, page, per_page, **kwargs):
        payload = json.dumps(
            {
                "query": query,
                "filter": {"visibility": visibility},
                "page": page,
                "perPage": per_page,
            }
        )
        return payload

    def create_collaboration(self, **kwargs):
        """kwargs should be like this:
        title="test",
        description="test",
        landingLink="https://test.com",
        displayType="withoutProducts[withProducts]",
        visible=1[0],
        isVisibleOnMainPage=1[0],
        type="option",
        userId=1,
        compilationId=
        images[desktop]="file"
        images[mobile]="file"
        """

        data = {}
        if "title" in kwargs:
            if kwargs["title"] is not None:
                data["title"] = kwargs.pop("title")
        else:
            data["title"] = Text("ru").sentence()[:255]

        if "description" in kwargs:
            if kwargs["description"] is not None:
                data["description"] = kwargs.pop("description")
        else:
            data["description"] = Text("ru").sentence()[:255]

        if "landingLink" in kwargs:
            if kwargs["landingLink"] is not None:
                data["landingLink"] = kwargs.pop("landingLink")
        else:
            data["landingLink"] = Internet().url()

        if "displayType" in kwargs:
            if kwargs["displayType"] is not None:
                data["displayType"] = kwargs.pop("displayType")
        else:
            data["displayType"] = "withoutProducts"

        if "visible" in kwargs:
            if kwargs["visible"] is not None:
                data["visible"] = kwargs.pop("visible")
        else:
            data["visible"] = "1"

        if "isVisibleOnMainPage" in kwargs:
            if kwargs["isVisibleOnMainPage"] is not None:
                data["isVisibleOnMainPage"] = kwargs.pop("isVisibleOnMainPage")
        else:
            data["isVisibleOnMainPage"] = "0"

        if "type" in kwargs:
            if kwargs["type"] is not None:
                data["type"] = kwargs.pop("type")
        else:
            data["type"] = random.choice(list(CollabType)).value

        if "userId" in kwargs:
            if kwargs["userId"] is not None:
                data["userId"] = kwargs.pop("userId")
        else:
            data["userId"] = "252"

        if "compilationId" in kwargs:
            data["compilationId"] = kwargs.pop("compilationId")

        return data

    def update_collaboration(self, **kwargs):
        """kwargs should contain current_data"""
        data_for_update = {}
        current_data = kwargs.pop("current_data") if "current_data" in kwargs else {}

        if len(current_data.keys()) > 0:
            for key in current_data:
                if key in ["compilation", "user"]:
                    if current_data[key] is not None:
                        data_for_update[f"{key}Id"] = current_data[key]["id"]
                        continue
                    else:
                        continue
                if key in ["visible", "isVisibleOnMainPage"]:
                    data_for_update[key] = 1 if current_data[key] is True else 0
                    continue
                if key in ["images", "id"]:
                    continue
                data_for_update[key] = current_data[key]
        else:
            data_for_update = dict(
                {
                    "title": Text("ru").sentence()[:255],
                    "landingLink": Internet().url(),
                    "displayType": "withoutProducts",
                    "visible": 1,
                    "isVisibleOnMainPage": 0,
                    "type": random.choice(list(CollabType)).value,
                }
            )
        if kwargs:
            for key in kwargs:
                if kwargs[key] is None:
                    data_for_update.pop(key)
                    continue
                data_for_update[key] = kwargs[key]

        return data_for_update

    def files(self, **kwargs):
        files = {}

        if "images" in kwargs:
            if kwargs["images"] is not None:
                files = kwargs.pop("images")
        else:
            files = utils.set_collaboration_images()

        return files
