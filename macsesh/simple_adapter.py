"""Provides an adapter for requests which uses the macOS keychain."""


import requests
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

from . import keychain
from .util import extract_from_urllib3


class SimpleKeychainAdapter(requests.adapters.HTTPAdapter):
    """Loads cadata from the keychain early to avoid using certifi"""

    def __init__(self, **kwargs):
        extract_from_urllib3()
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.load_verify_locations(cadata=keychain.get_truststore_data())
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context()
        context.load_verify_locations(cadata=keychain.get_truststore_data())
        kwargs['ssl_context'] = context
        return super().proxy_manager_for(*args, **kwargs)
