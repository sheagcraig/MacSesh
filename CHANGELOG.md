# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] 2022-02-11
### Changed
- Pared down pyobjc dependencies to just pyobjc-framework-SecurityFoundation.

## [0.3.0] 2020-05-22
### Added
- Added client cert auth using keychain identities to `SecureTransportAdapter`.

### Changed
- Renamed `SecureTransportSession` to `Session` to indicate that it's the one you probably want to use.
- Updated documentation accordingly.

## [0.2.1] 2020-04-28
### Added
- Reworked to simplify usage, and add alternate strategies.

## [0.1.0] 2020-04-25
### Added
- Initial MacKeychainTransportAdapter source.

[Unreleased]: https://github.com/sheagcraig/MacSesh/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/sheagcraig/MacSesh/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/sheagcraig/MacSesh/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/sheagcraig/MacSesh/compare/v0.1.0...v0.2.1
[0.1.0]: https://github.com/sheagcraig/MacSesh/releases/tag/v0.1.0