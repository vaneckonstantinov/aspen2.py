try:
    import setuptools  # noqa
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import find_packages, setup

from build import ASPEN_DEPS, TEST_DEPS

version = open('version.txt').read()


classifiers = [ 'Development Status :: 4 - Beta'
              , 'Environment :: Console'
              , 'Intended Audience :: Developers'
              , 'License :: OSI Approved :: MIT License'
              , 'Natural Language :: English'
              , 'Operating System :: OS Independent'
              , 'Programming Language :: Python :: 2.7'
              , 'Programming Language :: Python :: Implementation :: CPython'
              , 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
               ]

setup( author = 'Chad Whitacre et al.'
     , author_email = 'team@aspen.io'
     , classifiers = classifiers
     , description = 'A filesystem router for Python web frameworks'
     , name = 'aspen'
     , packages = find_packages()
     , url = 'https://github.com/AspenWeb/aspen.py'
     , version = version
     , zip_safe = False
     , package_data = {'aspen': ['request_processor/mime.types']}
     , install_requires = ASPEN_DEPS
     , tests_require = TEST_DEPS
      )
