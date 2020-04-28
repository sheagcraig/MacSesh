"""Provides an adapter for requests which SecureTransport

This is how pip does it, plus a little override to the cert_verify
method to force it to use our keychain certs instead of certifi's.

"""


import requests
import urllib3.contrib.securetransport


class SecureTransportAdapter(requests.adapters.HTTPAdapter):
    """HTTPAdapter that uses macOS SecureTransport"""

    def __init__(self, **kwargs):
        urllib3.contrib.securetransport.inject_into_urllib3()
        super().__init__(**kwargs)

    def cert_verify(self, conn, url, verify, cert):
        if url.lower().startswith('https') and verify:
            conn.cert_reqs = 'CERT_REQUIRED'
        else:
            super().cert_verify(conn, url, verify, cert)
