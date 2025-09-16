from voluptuous import PREVENT_EXTRA, ALLOW_EXTRA, Schema, Boolean, Any

update_user_request_schema = Schema(
    {
        "about": Any(str, None),
        "userName": Any(str, None),
        "portfolioUrl": Any(str, None),
        "telegramLink": Any(str, None),
        "vkLink": Any(str, None),
        "specialization": Any(str, None),
        "city": Any(str, None),
    },
    extra=ALLOW_EXTRA,
)

auth_user_response = Schema(
    {
        "data": {
            "id": int,
            "customerId": int,
            "type": "Bearer",
            "token": str,
            "expiresAt": str,
        },
        "status": str,
    },
    extra=PREVENT_EXTRA,
    required=True,
)

user_data_response = Schema(
    {
        "data": {
            "id": int,
            "customerId": int,
            "userName": Any(str, None),
            "firstName": str,
            "lastName": str,
            "phone": str,
            "email": str,
            "city": Any(str, None),
            "photo": Any(str, None),
            "about": Any(str, None),
            "specialization": Any(str, None),
            "portfolioUrl": Any(str, None),
            "telegramLink": Any(str, None),
            "vkLink": "https://vk.com/alena.potegova",
            "worksCount": 0,
            "isVerified": Boolean,
            "isVoter": Boolean,
            "worksInContests": [],
        },
        "status": "OK",
    },
    extra=PREVENT_EXTRA,
    required=True,
)

avatar_update_response = Schema(
    {"data": {"photo": str}, "status": str},
    extra=PREVENT_EXTRA,
    required=True,
)

avatar_delete_response = Schema(
    {"data": ["Deleted"], "status": str},
    extra=PREVENT_EXTRA,
    required=True,
)

users_likes = Schema(
    {"data": {"works": [], "contests": []}, "status": str},
    extra=PREVENT_EXTRA,
    required=True,
)
