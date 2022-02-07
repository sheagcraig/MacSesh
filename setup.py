import pathlib
from setuptools import setup


project_dir = pathlib.Path(__file__).parent.resolve()
readme = project_dir / 'README.md'
namespace = {}
version_path = project_dir / 'macsesh/version.py'
exec(version_path.read_text(), namespace)

setup(
    name='MacSesh',
    version=namespace['__version__'],
    packages=['macsesh'],
    license='GPLv3',
    description='Tools for letting the macOS Keychain verify certs for python requests',
    long_description=readme.read_text(),
    long_description_content_type='text/markdown',
    author='Shea G. Craig',
    author_email='sheagcraig@gmail.com',
    url='https://github.com/sheagcraig/MacSesh',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: MacOS X :: Cocoa',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3 :: Only'
    ],
    install_requires=['requests', 'pyobjc-framework-SecurityFoundation', 'six'],
    python_requires='>=3.6',
)
