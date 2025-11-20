"""Provides an adapter for requests which SecureTransport

This is how pip does it, although we add two features here:
1. A little override to the cert_verify method to force it to use our
   keychain certs instead of certifi's.
2. An override to use the keychain for certificate auth.
"""


from ctypes import byref
from operator import itemgetter

import objc
import requests
from . import securetransport
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from Security import (
    SecCertificateCopyValues,
    SecIdentityCopyCertificate,
    SecItemCopyMatching,
    errSecSuccess,
    kSecClass,
    kSecClassIdentity,
    kSecMatchLimit,
    kSecMatchLimitAll,
    kSecMatchSubjectContains,
    kSecOIDCommonName,
    kSecOIDX509V1SubjectName,
    kSecOIDX509V1ValidityNotAfter,
    kSecReturnRef)
from ._securetransport.bindings import CoreFoundation, Security
from ._securetransport.low_level import _cf_dictionary_from_tuples

from . import keychain


class SecureTransportAdapter(requests.adapters.HTTPAdapter):
    """HTTPAdapter that uses macOS SecureTransport"""

    def __init__(self, **kwargs):
        securetransport.inject_into_urllib3()
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        # Override poolmanager setup to stash a copy of the context
        # for later access.
        self.context = create_urllib3_context()
        kwargs['ssl_context'] = self.context
        return super().init_poolmanager(*args, **kwargs)

    def cert_verify(self, conn, url, verify, cert):
        if url.lower().startswith('https') and verify:
            conn.cert_reqs = 'CERT_REQUIRED'
        else:
            super().cert_verify(conn, url, verify, cert)
        if cert:
            self.context.load_cert_chain(cert)


def _load_client_cert_chain(_, name, *paths):
    """Load certs by SN from keychain rather than by path

    If multiple certs are found which contain the provided name, the
    one that has an exactly equivalent CN, and with the latest "not
    valid after" date will be chosen.

    Args:
        _ (keychain): Unused; here to support injecting into existing code.
        name (str): CN to match.
        paths: Any number of str paths, only the first of which will be used.

    Returns:
        CFMutableArray
    """
    # Create an array to return
    trust_chain = CoreFoundation.CFArrayCreateMutable(
        CoreFoundation.kCFAllocatorDefault,
        0,
        byref(CoreFoundation.kCFTypeArrayCallBacks),)

    query = {
        kSecClass: kSecClassIdentity,
        kSecMatchLimit: kSecMatchLimitAll,
        kSecMatchSubjectContains: name,
        kSecReturnRef: True,
    }
    error, results = SecItemCopyMatching(query, None)
    if error == errSecSuccess:
        candidates = []
        for identity in results:
            error, cert_ref = SecIdentityCopyCertificate(identity, None)
            if error == errSecSuccess:
                cert_info, error  = SecCertificateCopyValues(cert_ref, None, None)
                if error is None and _get_cn(cert_info) == name:
                    not_valid_after = cert_info[kSecOIDX509V1ValidityNotAfter]['value']
                    candidates.append((not_valid_after, identity))

        try:
            current_identity = sorted(candidates, key=itemgetter(0))[-1][1]
            CoreFoundation.CFArrayAppendValue(trust_chain, objc.pyobjc_id(current_identity))
        except IndexError:
            # No candidates matched.
            pass

    return trust_chain


def _get_cn(cert_info):
    name = ''
    for i in cert_info[kSecOIDX509V1SubjectName]['value']:
        if i['label'] == kSecOIDCommonName:
            name = i['value']
    return name


# Monkey patch!
securetransport._load_client_cert_chain = _load_client_cert_chain
