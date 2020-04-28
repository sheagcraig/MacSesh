"""Utilities for reverting the changes we made to urllib3"""


import requests.api
from requests.packages.urllib3 import util as urllib3_util


# Store the original values of these urllib3 attributes so we can
# restore them later.
ORIGINAL_HAS_SNI = urllib3_util.HAS_SNI
ORIGINAL_SSLContext = urllib3_util.ssl_.SSLContext
# Store the original requests API funcs so we can restore later.
ORIGINAL_REQUEST = requests.api.request


def extract_from_urllib3():
    """Undo the injection of this project's contexts from urllib3"""
    urllib3_util.SSLContext = ORIGINAL_SSLContext
    urllib3_util.ssl_.SSLContext = ORIGINAL_SSLContext
    urllib3_util.HAS_SNI = ORIGINAL_HAS_SNI
    urllib3_util.ssl_.HAS_SNI = ORIGINAL_HAS_SNI
    urllib3_util.IS_SECURETRANSPORT = False
    urllib3_util.ssl_.IS_SECURETRANSPORT = False


def inject_into_requests(session_class=None):
    """Inject a different Session class into requests' basic API

    e.g. to use the KeychainSession for requests.get, requests.post, etc
    ```
    >>> inject_into_api(KeychainSession)
    >>> requests.get('https://nethack.org')
    ```

    Args:
        session_class: requests.Session or subclass to use for one-off
            requests. Defaults to `KeychainSession`
    """
    # Handle the default class here by importing late to avoid circular
    # import issues.
    if not session_class:
        from .session import KeychainSession
        session_class = KeychainSession
    # Create a func that replicates requests.api.request, just subbing
    # in the passed session class as a kind of closure.
    def request(method, url, **kwargs):
        with session_class() as session:
            return session.request(method=method, url=url, **kwargs)

    requests.api.request = request


def extract_from_requests():
    """Restore requests' original Session class to basic API"""
    requests.api.request = ORIGINAL_REQUEST
