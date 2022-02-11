# MacSesh
This package allows the popular requests library to use the macOS
keychain for both validating a server, and for doing client cert auth.
Its original use-case was for Mac admins wanting to use python requests
and certs provided by an MDM for TLS, Specifically, SCEP certs client 
cert auth and x509 payloads for server validation.

### Installing

```
pip install MacSesh
```

If you want to install from a source distribution, clone and run below. 

```
pip install .
```

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

## Validating a server
macsesh uses any of the _trusted_ certs from keychains included in the
current user's keychain search list, as well as the system roots.
Typically, this search list consists of:
- The user's default keychain at `~/Library/Keychains/login.keychain`
- The system keychain at `/Library/Keychains/System.keychain`
- The System Roots keychain at
  `/System/Library/Keychains/SystemRootCertificates.keychain`.

Certs in the system roots are implicitly trusted. Certs from other
keychains must be marked as trusted for this purpose or they won't be
included.

When using macsesh, just leave the requests `verify` at its default of
`True` and macsesh will do the rest.

## Client cert auth
macsesh can also do client cert auth from the keychain, currently only
with the `SecureTransportAdapter`. The other adapter types can do client
cert auth as well of course, but they require the identity to be
available on the filesystem just like regular requests.

To specify a certificate to use, provide the Common Name of the cert to
requests' normal `cert` argument as in the example above. As the keychain
may have multiple certs which match , macsesh performs some additional 
filtering.
1. The query does a "subject contains" search with the CN provided, so
   for exmaple `cert='taco'` could match a CN of `taco truck` or `taco
   party`. macsesh will drop anything that is not an exact match.
2. The resulting certs may have been renewed, and the old certs are still
   in the keychain. macsesh sorts them by "not valid after" date and
   picks the one with the longest lifespan.

## Advanced

### Cleanup
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

### Choosing a session type
macsesh provides three different types of requests `Session` classes.
While we probably only need the `Session`, the other two are included for
posterity since they are interesting and potentially useful.

1. If in doubt, use `Session` It uses the securetransport module
   contributed to urllib3 as a base SSLContext. Pip, for example, uses
   this on macOS.  The securetransport module uses an entirely different
   `SSLContext`, using ctypes to connect to the macOS `Security` 
   framework. macsesh then injects additional code into the urllib3
   code to use the keychain instead of conforming to the OpenSSL approach
   of using paths to files. If you need to do client cert auth from
   keychain identities, this is the one you want.
1. `KeychainSession` uses a custom SSLContext, requests Adapter, and
   requests Session, and injects the SSLContext into urllib3. The certs
   for validation are dumped from the keychain and held in memory. The
   goal of this approach is to use the minimum amount of messing about to
   achieve cert validation.
3. `SimpleKeychainSession` circumvents the normal flow of session
   startup, and tells the SSLContext to load its trust information
   up front rather than waiting for a bunch of internal checks to decide
   the context needs to load the trust store. It uses the same method
   as the `KeychainSession` and functionally shouldn't be any different.

### What about cert auth for `SimpleKeyhainSession` and
`KeychainSession`?

I can try implementing looking up and retrieving certs by name for the
other "strategies", but I'm not sure how much utility there is for that,
as the keys would have to be exportable. At that point, just export them
and use regular old requests.
