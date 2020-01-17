"""Importing this package will upgrade the `backslashreplace` error handling
scheme in the global `codecs` registry to support handling decoding errors as
well as encoding errors.
"""
from . import backcompat

backcompat.upgrade_backslashreplace()
