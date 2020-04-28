"""requests Session classes for three different keychain strategies"""


import requests

from .injected_adapter import KeychainAdapter
from .secure_transport_adapter import SecureTransportAdapter
from .simple_adapter import SimpleKeychainAdapter


class KeychainSession(requests.Session):
    """Requests session using the injected KeychainAdapter"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mount('https://', KeychainAdapter())


class SecureTransportSession(requests.Session):
    """Requests session using the SecureTransport"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mount('https://', SecureTransportAdapter())


class SimpleKeychainSession(requests.Session):
    """Requests session using the SimpleKeychainAdapter"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mount('https://', SimpleKeychainAdapter())
