import os
from dotenv import load_dotenv
from utils.base_session import BaseSession
from utils.auth import get_token

load_dotenv()

private_api_url = os.getenv("PRIVATE_API_URL")
public_api_url = os.getenv("PUBLIC_API_URL")
internal_api_url = os.getenv("INTERNAL_API_URL")
orders_api_url = os.getenv("ORDERS_API_URL")
orders_private_api_url = os.getenv("ORDERS_PRIVATE_API_URL")
monolith_api_url = os.getenv("MONOLITH_API_URL")
esb_api_url = os.getenv("ESB_URL")
api_key_esb = os.getenv("ESB_TOKEN")
auth_api_url = os.getenv("AUTH_API_URL")
public_host_url = os.getenv("PUBLIC_HOST_URL")
client_catalog = os.getenv("CLIENT_CATALOG")
secret_catalog = os.getenv("SECRET_CATALOG")
client_cocr = os.getenv("CLIENT_COCREATE")
secret_cocr = os.getenv("SECRET_COCREATE")
private_auth_token = get_token(auth_api_url, client_catalog, secret_catalog)
private_auth_token_cocr = get_token(auth_api_url, client_cocr, secret_cocr)
api_key = private_auth_token
api_key_cocr = private_auth_token_cocr
api_key_internal = os.getenv("API_KEY_INTERNAL")
front_url = os.getenv("SHOP_URL")
cocreate_private_api_url = os.getenv("COCREATE_PRIVATE_API_URL")
cocreate_public_api_url = os.getenv("COCREATE_PUBLIC_API_URL")

config_public_api_url = os.getenv("CONFIG_PUBLIC_API_URL")
config_private_api_url = os.getenv("CONFIG_PRIVATE_API_URL")
config_internal_api_url = os.getenv("CONFIG_INTERNAL_API_URL")
api_key_internal_config = os.getenv("API_KEY_INTERNAL_CONFIG")

private_session = BaseSession(base_url=private_api_url, api_key=api_key)
public_session = BaseSession(base_url=public_api_url)
internal_session = BaseSession(base_url=internal_api_url, api_key=api_key_internal)
orders_session = BaseSession(base_url=orders_api_url)
orders_private_session = BaseSession(base_url=orders_private_api_url, api_key=api_key)
monolith_session = BaseSession(base_url=monolith_api_url)
esb_session = BaseSession(base_url=esb_api_url, api_key=api_key_esb, type="basic")
storage_session = BaseSession(base_url=public_host_url)
cocreate_private_session = BaseSession(
    base_url=cocreate_private_api_url, api_key=api_key_cocr
)
front_session = BaseSession(base_url=front_url)
cocreate_public_session = BaseSession(base_url=cocreate_public_api_url)

config_public_session = BaseSession(base_url=config_public_api_url)
config_private_session = BaseSession(base_url=config_private_api_url, api_key=api_key)
config_internal_session = BaseSession(base_url=config_internal_api_url, api_key=api_key_internal_config)
