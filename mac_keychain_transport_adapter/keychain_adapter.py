"""Provides an adapter for requests which uses the macOS keychain."""


import itertools
import pathlib
import tempfile
from typing import Optional

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

    Params:
        truststore_path: Optional[str] By default KeychainAdapter uses a
            tempfile to write out the certificate contents. This param
            allows you to use the path of your choosing. However, keep
            in mind that the path will be overwritten by the keychain
            contents whenever the `update_truststore` method is called,
            including during the first request made using this adapter.

    Methods:
        update_truststore: Regenerates the truststore contents. Only
            needed if the keychain has changed since the `Session`
            was instantiated and the adapter mounted.

    Properties:
        truststore: None (use a tempfile) or a path to the location to
            save PEM contents. This file will be overwritten!

    Usage:
    ```
    >>> sesh = requests.Session()
    >>> adapter = KeychainAdapter()
    >>> sesh.mount('https://', adapter)
    >>> response = sesh.get('https://nethack.org')
    ```
    """

    _truststore: Optional[str] = None

    def __init__(self, truststore_path: Optional[str] = None, **kwargs):
        self.truststore = truststore_path
        super().__init__(**kwargs)

    @property
    def truststore(self):
        return self._truststore

    @truststore.setter
    def truststore(self, path: Optional[str]):
        if path is None or isinstance(path, (str, pathlib.Path)):
            self._truststore = path
            self.update_truststore()
        else:
            raise ValueError()


    def cert_verify(self, conn, url, verify, cert):
        """Manage urllib3 truststore parameters."""
        # Override cert_verify to use macOS keychain

        # If verify is True, we should use the keychain for verifying
        # SSL certs.
        if not isinstance(verify, bool):
            raise ValueError(
                "The KeychainAdapter transport does not support paths to CA bundles. Use a "
                "regular HTTPAdapter (the default)!")
        elif verify is True:
            if pathlib.Path(self._truststore).exists():
                conn.cert_reqs = 'CERT_REQUIRED'
                conn.ca_certs = self._truststore
        elif verify is False:
            super().cert_verify(conn, url, verify, cert)
        else:
            raise ValueError('Inappropriate argument for `verify`.')

    def update_truststore(self):
        """Queries the keychain for all currently trusted certs

        Regenerates the truststore contents. Only needed if the keychain
        has changed since the `Session` was instantiated and the adapter
        mounted.

        Since urllib3 expects a _path_ to a truststore, this method
        writes the PEM files to the truststore path configured on this
        adapter (by default a tempfile).
        """
        certs = itertools.chain(self._get_trusted_certs(), self._get_system_roots())
        return_code, pem_data = SecItemExport(
            list(certs), kSecFormatUnknown, kSecItemPemArmour, None, None)
        if return_code == errSecSuccess:
            if self._truststore is None:
                with tempfile.NamedTemporaryFile('w+b', delete=False) as handle:
                    handle.write(pem_data)
                    self._truststore = handle.name
            else:
                pathlib.Path(self._truststore).write_bytes(pem_data)

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
