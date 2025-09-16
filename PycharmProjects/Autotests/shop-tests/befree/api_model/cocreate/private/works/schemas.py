from voluptuous import PREVENT_EXTRA, ALLOW_EXTRA, Schema, Boolean, Any

cms_work = Schema(
    {
        "data": {
            "id": int,
            "title": str,
            "description": Any(str, None),
            "likes": int,
            "isWinner": Boolean,
            "isAudienceWinner": Boolean,
            "rejectReason": Any(str, None),
            "visible": Boolean,
            "cover": str,
            "images": list,
            "contest": Any(
                {
                    "id": int,
                    "title": str,
                    "status": {"key": str, "value": str},
                    "visible": Boolean,
                    "createdAt": str,
                },
                None,
            ),
            "user": {
                "id": int,
                "firstName": str,
                "lastName": str,
                "email": str,
                "photo": Any(str, None),
            },
            "status": {"key": str, "value": str},
        },
        "status": "OK",
    },
    extra=PREVENT_EXTRA,
    required=True,
)

cms_work_update = Schema(
    {"visible": Boolean, "status": str, "isWinner": Boolean, "rejectReason": str},
    extra=ALLOW_EXTRA,
    required=False,
)
