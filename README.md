# Mac Keychain Transport Adapter
This package provides a transport adapter for requests that allows you to verify SSL certificates with
trusted certificates from the macOS keychain.

## Usage
Usage is simple:
```
import requests
from mac_keychain_transport_adapter import KeychainAdapter

# Setup
sesh = requests.Session()
keychain = KeychainAdapter()
sesh.mount('https://', keychain)

# Get stuff done!
response = sesh.get('https://nethack.org/')
```
