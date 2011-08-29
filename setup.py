from distutils.core import setup

setup (
    author='Mathias Ruediger',
    author_email='ruediger@informatik.uni-marburg.de',
    name='MarvinFilesystem',
    version='0.1',
    packages=['mfs','mfs/manifest'],
    scripts=['mfsserver.py','mfsclient.py','mfsmanager.py']
)
