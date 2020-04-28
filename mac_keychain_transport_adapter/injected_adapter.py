"""Provides an adapter for requests which uses the macOS keychain."""


import ssl

import requests
from requests.packages.urllib3 import util

from . import keychain


class KeychainContext(ssl.SSLContext):
    """SSLContext that reads its trust data from the macOS keychain"""

    def load_default_certs(self, purpose=ssl.Purpose.SERVER_AUTH):
        """Load user, system, and root trusted certs from keychain"""
        self.load_verify_locations(cadata=keychain.get_truststore_data())


class KeychainAdapter(requests.adapters.HTTPAdapter):
    """HTTPAdapter that uses the macOS keychain for cert verification"""

    def __init__(self, **kwargs):
        inject_into_urllib3()
        super().__init__(**kwargs)

    def cert_verify(self, conn, url, verify, cert):
        if url.lower().startswith('https') and verify is True:
            conn.cert_reqs = 'CERT_REQUIRED'
            # The super sees that no ca data is available yet and then
            # figures out the location of the default truststore,
            # certifi. We don't want that. Even though the ca certs
            # don't actually get loaded until much later, letting
            # ca_path get set here persists up through that point and
            # prevents our KeychainContext.load_default_certs from ever
            # getting called. (See requests' bundled
            # urllib3.connection.HTTPConnection.connect to see where
            # the initial SSLContext for a connection is set up and
            # triggered into loading certs).
        else:
            super().cert_verify(conn, url, verify, cert)


def inject_into_urllib3():
    """Replace urllib3 SSLContext with our KeychainContext"""
    util.SSLContext = KeychainContext
    util.ssl_.SSLContext = KeychainContext
