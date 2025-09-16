from voluptuous import PREVENT_EXTRA, ALLOW_EXTRA, Schema, Boolean, Any

cms_users_list = Schema(
    {
        "data": {"users": [{"id": int, "firstName": str, "lastName": str, "email": str}]},
        "status": str,
        "pagination": {
            "total": int,
            "perPage": int,
            "currentPage": int,
            "lastPage": int,
        },
    },
    extra=PREVENT_EXTRA,
    required=True,
)

cms_user = Schema(
    {
        "data": {
            "id": int,
            "userName": Any(str, None),
            "firstName": str,
            "lastName": str,
            "email": str,
            "phone": str,
            "gender": str,
            "city": Any(str, None),
            "description": Any(str, None),
            "portfolio": Any(str, None),
            "specialization": Any(str, None),
            "vk": Any(str, None),
            "telegram": Any(str, None),
            "birthDate": str,
            "isCreator": Boolean(),
            "isVoter": Boolean(),
            "hasVerification": Boolean(),
        },
        "status": str,
    },
    extra=PREVENT_EXTRA,
    required=True,
)
