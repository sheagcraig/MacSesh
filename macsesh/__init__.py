"""This package allows requests to verify certs with the macOS keychain

It uses any trusted certs from keychains included in the current
user's keychain search list, as well as the system roots. Typically,
this is the user's default at ~/Library/Keychains/login.keychain,
the system keychain at /Library/Keychains/System.keychain, and the
System Roots keychain at
/System/Library/Keychains/SystemRootCertificates.keychain.

To achieve this, one of three different strategies can be employed:
1. KeychainSession uses a custom SSLContext, requests Adapter, and
   requests Session, and injects the SSLContext into urllib3. This
   approach is the recommendation.
2. SecureTransportSession uses the urllib3 contrib module for injecting
   SecureTransport equivalents into stock urllib3. While this approach
   uses more of the native networking framework, it also seems to be
   written primarily with the goal of solving the issues with macOS and
   aging OpenSSL versions to ensure that Macs could still use pip.
   Therefore, it's not entirely feature-complete in providing a full
   requests Adapter. It's definitely worth experimenting with.
3. SimpleKeychainSession circumvents the normal flow of session
   startup, and tells the SSLContext to load its trust information
   early; in this case from certs dumped from the keychain.

Example Usage:
```
>>> import macsesh
>>> sesh = macsesh.KeychainSession()
>>> response = sesh.get('https://nethack.org')
```
Note: if you want to revert to "normal" requests (probably using
certifi), in the same python process, you'll need to remove this
module's injected stuff from urllib3:
```
>>> macsesh.extract_from_urllib3()
```

Finally, any certs added to the keychains after starting a session will
not be available. The sessions and adapters all have an update_truststore
method for re-dumping the trust.
"""
from .keychain import get_trusted_certs, get_truststore_data, get_system_roots
from .injected_adapter import KeychainAdapter, KeychainContext
from .secure_transport_adapter import SecureTransportAdapter
from .session import KeychainSession, SecureTransportSession, SimpleKeychainSession
from .simple_adapter import SimpleKeychainAdapter
from .util import extract_from_urllib3, inject_into_requests, extract_from_requests
from .version import __version__
