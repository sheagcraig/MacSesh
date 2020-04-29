# MacSesh
This package allows requests to verify certs with the macOS keychain,
rather than using certifi. It also includes some tools for easily
hooking up a `SecureTransport` adapter (a la Pip) and then later
undoing all of the sneaky infiltrations required to set this up.

## Which certs?
It uses any of the trusted certs from keychains included in the current
user's keychain search list, as well as the system roots. Typically,
this is the user's default at `~/Library/Keychains/login.keychain`,
the system keychain at `/Library/Keychains/System.keychain`, and the
System Roots keychain at
`/System/Library/Keychains/SystemRootCertificates.keychain`.

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

## Example Usage:
```
>>> import macsesh
>>> sesh = macsesh.KeychainSession()
>>> response = sesh.get('https://nethack.org')
```
If you want to use the "basic" requests API without creating a session:
```
>>> macsesh.inject_into_requests()
>>> requests.get('https://en.wikipedia.org/wiki/Taco')  # Uses keychain
```

## Advanced
If for some reason you want to revert to "normal" requests (probably 
using certifi), in the same python process, you'll need to remove this
module's injected stuff from urllib3 or requests.

Remove the SSLContext if you used any of the Sessions:
```macsesh.extract_from_urllib3()```
Clean up after using the "basic" API:
```macsesh.extract_from_requests()```

Any certs added to the keychains after starting a session will
not be available. Digging down in and updating the SSLContext is rough;
just make a new session if you have this need!