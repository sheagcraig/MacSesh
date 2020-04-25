"""Provides an adapter for requests which uses the macOS keychain."""


import itertools
import pathlib
import tempfile

import requests
# pylint: disable=E0611
from Security import (
    errSecSuccess, kSecClass, kSecReturnRef, kSecMatchLimit, kSecMatchLimitAll,
    SecItemCopyMatching, kSecClassCertificate, kSecMatchTrustedOnly, SecKeychainOpen,
    kSecMatchSearchList, SecItemExport, kSecFormatUnknown, kSecItemPemArmour)
# pylint: enable=E0611

class KeychainAdapter(requests.adapters.HTTPAdapter):
    """This adapter for requests verifies certs with the macOS keychain

    It uses any trusted certs from keychains included in the current
    user's keychain search list, as well as the system roots.

    To use:
    ```
    >>> sesh = requests.Session()
    >>> adapter = KeychainAdapter()
    >>> sesh.mount('https://', adapter)
    >>> response = sesh.get('https://nethack.org')
    ```
    """

    _truststore = None

    def cert_verify(self, conn, url, verify, cert):
        # Override cert_verify to use macOS keychain

        # If verify is True, we should use the keychain for verifying
        # SSL certs.
        if verify is True:
            self._build_truststore()
            if pathlib.Path(self._truststore).exists():
                conn.cert_reqs = 'CERT_REQUIRED'
                conn.ca_certs = self._truststore
        # Otherwise, the verify arg is either:
        # a.) False: don't verify. Fall back to superclass.
        # b.) Path to a pem file/dir: just let the superclass handle it.
        else:
            super().cert_verify(conn, url, verify, cert)

    def _build_truststore(self):
        certs = itertools.chain(self._get_trusted_certs(), self._get_system_roots())
        return_code, pem_data = SecItemExport(
            list(certs), kSecFormatUnknown, kSecItemPemArmour, None, None)
        if return_code == errSecSuccess:
            with tempfile.NamedTemporaryFile('w+b', delete=False) as handle:
                handle.write(pem_data)
                self._truststore = handle.name

    def _get_trusted_certs(self):
        """Return all trusted certs in the default keychain search

        By default, this includes the user's keychain and the sytem
        keychain.

        This ONLY returns trusted certs!

        Returns:
            List of dicts with keys:
                v_Data: Raw cert data
                v_Ref: Reference to certificate.
            Empty list if there are no results (odd) or there's an error.
        """
        query = {
            kSecClass: kSecClassCertificate,
            kSecReturnRef: True,
            kSecMatchLimit: kSecMatchLimitAll,
            kSecMatchTrustedOnly: True
        }

        result_code, result = SecItemCopyMatching(query, None)
        return result if result_code == errSecSuccess else []

    def _get_system_roots(self):
        """Return all certs from the macOS SystemRoots.

        These certs are trusted implicitly by dint of being in this keychain.

        Returns:
            List of dicts with keys:
                v_Data: Raw cert data
                v_Ref: Reference to certificate.
            Empty list if there are no results (odd) or there's an error.
        """
        return_code, system_roots_keychain = SecKeychainOpen(
            b"/System/Library/Keychains/SystemRootCertificates.keychain", None)
        if not return_code == errSecSuccess:
            return []
        query = {
            kSecClass: kSecClassCertificate,
            kSecReturnRef: True,
            kSecMatchLimit: kSecMatchLimitAll,
            kSecMatchSearchList: [system_roots_keychain]
        }
        result_code, result = SecItemCopyMatching(query, None)
        return result if result_code == errSecSuccess else []
