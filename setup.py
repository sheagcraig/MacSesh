import pathlib
from setuptools import setup


project_dir = pathlib.Path(__file__).parent.resolve()
readme = project_dir / 'README.md'
namespace = {}
version_path = project_dir / 'mac_keychain_transport_adapter/version.py'
exec(version_path.read_text(), namespace)

setup(
    name='MacKeychainTransportAdapter',
    version=namespace['__version__'],
    packages=['mac_keychain_transport_adapter'],
    license='GPLv3',
    description='A Requests Transport Adapter which verifies SSL certs using the macOS Keychain',
    long_description=readme.read_text(),
    long_description_content_type='text/markdown',
    author='Shea G. Craig',
    author_email='sheagcraig@gmail.com',
    url='https://github.com/sheagcraig/MacKeychainTransportAdapter',
)