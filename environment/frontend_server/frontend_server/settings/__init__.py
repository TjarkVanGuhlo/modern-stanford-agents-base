###FOR PUSHING STATIC TO AWS


# from .base import *
# from .production import *

# try:
#   from .local import *
# except:
# pass


###FOR GENERAL USES

# ruff: noqa: F403 - Star imports are idiomatic for Django settings
from .base import *

try:
    from .local import *

    live = False
except Exception:
    live = True

if live:
    from .production import *
