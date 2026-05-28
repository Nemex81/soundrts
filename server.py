#! .venv\Scripts\python.exe
# UI-MASTER-07/P0-OPTIONS-FIX: see soundrts.py for the rationale —
# command-line parsing must run before importing the server module
# so that ``options.port`` is bound to the override (if any) before
# ``servermain`` captures it as a default argument value.
from soundrts import options

options.parse_args()

from soundrts import server

server.main()
