from distutils.core import setup

setup (
    author='Mathias Ruediger',
    author_email='ruediger@informatik.uni-marburg.de',
    name='MARVIN-Image-Store',
    version='0.1',
    packages=['mis','mis/manifest'],
    scripts=['misserver','misclient','mismanager']
)
