"""requests Session classes for three different keychain strategies"""


import requests

from .injected_adapter import KeychainAdapter
from .secure_transport_adapter import SecureTransportAdapter
from .simple_adapter import SimpleKeychainAdapter


class BaseKeychainSession(requests.Session):

    _adapter_class = KeychainAdapter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mount('https://', self._adapter_class())


class KeychainSession(BaseKeychainSession):
    """Requests session using the injected KeychainAdapter"""

    _adapter_class = KeychainAdapter


class Session(BaseKeychainSession):
    """Requests session using the SecureTransport"""

    _adapter_class = SecureTransportAdapter


class SimpleKeychainSession(BaseKeychainSession):
    """Requests session using the SimpleKeychainAdapter"""

    _adapter_class = SimpleKeychainAdapter
