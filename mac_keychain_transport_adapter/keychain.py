"""Functions for getting trusted certificates from the macOS keychain"""


# pylint: disable=E0611
from Security import (
    errSecSuccess, kSecClass, kSecReturnRef, kSecMatchLimit, kSecMatchLimitAll,
    SecItemCopyMatching, kSecClassCertificate, kSecMatchTrustedOnly,
    SecItemExport, kSecFormatUnknown,
    SecTrustCopyAnchorCertificates)
# pylint: enable=E0611


def get_truststore_data():
    """Return PEM-encoded trusted certs from the keychain.

    Cats all of the certs from the user's keychain search list with
    all of the certs from the System Roots, then exports them as
    PEM-encoded x509 certificates.

    Returns:
        str of PEM-encoded trusted certs or empty str.:w
    """
    certs = get_trusted_certs()
    certs.extend(get_system_roots())
    return_code, pem_data = SecItemExport(certs, kSecFormatUnknown, 0, None, None)
    return bytes(pem_data).decode() if return_code == errSecSuccess else ''


def get_trusted_certs():
    """Return all trusted certs in the default keychain search

    By default, this includes the user's keychain and the system
    keychain.

    This ONLY returns trusted certs!

    Returns:
        List of SecCertificateRef.
        Empty list if there are no results (odd) or there's an error.
    """
    query = {
        kSecClass: kSecClassCertificate,
        kSecReturnRef: True,
        kSecMatchLimit: kSecMatchLimitAll,
        kSecMatchTrustedOnly: True
    }

    result_code, result = SecItemCopyMatching(query, None)
    return list(result) if result_code == errSecSuccess else []


def get_system_roots():
    """Return all certs from the macOS SystemRoots.

    These certs are trusted implicitly by dint of being in this keychain.

    Returns:
        List of SecCertificateRef.
    """
    result_code, result = SecTrustCopyAnchorCertificates(None)
    return list(result) if result_code == errSecSuccess else []
