"""MacSesh

This package allows the popular requests library to use the macOS
keychain for both validating a server, and for doing client cert auth.
Its original use-case was for Mac admins wanting to use python requests
and certs provided by an MDM for TLS, Specifically, SCEP certs client
cert auth and x509 payloads for server validation.

## Example Usage:
Validate using a trusted cert from the keychain:

```
>>> import macsesh
>>> sesh = macsesh.Session()
>>> response = sesh.get('https://nethack.org')
```
If you want to use the "basic" requests API without creating a session:

```
>>> macsesh.inject_into_requests()
>>> requests.get('https://en.wikipedia.org/wiki/Taco')  # Uses keychain
```

Client cert auth:

```
>>> import macsesh
>>> sesh = macsesh.Session()
>>> response = sesh.get('https://nethack.org', cert='My Identity Cert')
```
"""


from .injected_adapter import KeychainAdapter, KeychainContext
from .keychain import get_trusted_certs, get_truststore_data, get_system_roots
from .secure_transport_adapter import SecureTransportAdapter
from .session import KeychainSession, Session, SimpleKeychainSession
from .simple_adapter import SimpleKeychainAdapter
from .util import extract_from_urllib3, inject_into_requests, extract_from_requests
from .version import __version__
