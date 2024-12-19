import sys as _sys

name='openalpr'

if _sys.version_info.major >= 3:
    from .openalpr import Alpr
else:
    from openalpr import Alpr
