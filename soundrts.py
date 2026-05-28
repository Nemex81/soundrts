#! .venv\Scripts\python.exe
# UI-MASTER-07/P0-OPTIONS-FIX: parse command-line options BEFORE
# importing clientmain so that consumers binding ``options.port`` as a
# default argument value (e.g. ``clientserver.connect_and_play``) see
# the override at function-definition time.
from soundrts import options

options.parse_args()

from soundrts import clientmain

clientmain.main ()
