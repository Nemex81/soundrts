"""command line options"""

import optparse

from .lib.log import warning

ip = None
mods = None
soundpacks = None
port = 2500


def parse_args(argv=None):
    """Parse ``argv`` and update the module-level option globals.

    UI-MASTER-07/P0-OPTIONS-FIX: previously this function was invoked
    unconditionally at import time, so any sibling tool (pytest,
    sphinx, mypy) whose ``sys.argv`` contained tokens that did not
    match this parser would terminate the interpreter with
    ``SystemExit: 2`` before its own code could run. Entry points
    (``soundrts.py``, ``server.py``) now call ``parse_args()``
    explicitly *before* importing ``clientmain``/``servermain`` so that
    consumers binding ``options.port`` as a default argument value
    (e.g. ``clientserver.connect_and_play``) still see the
    command-line override.

    ``argv`` defaults to ``None`` which forwards to optparse's own
    ``sys.argv`` handling.
    """
    global ip, mods, soundpacks, port
    default_port = port
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ip", type="string")
    parser.add_option("-m", "--mods", type="string")
    parser.add_option("-s", "--soundpacks", type="string")
    parser.add_option("-p", type="int", help=optparse.SUPPRESS_HELP)
    parser.set_defaults(ip=None, mods=None, p=default_port, g=False)
    options, _ = parser.parse_args(argv)
    ip = options.ip
    mods = options.mods
    soundpacks = options.soundpacks
    port = options.p
    if ip:
        warning("using IP %s", ip)
    if port != default_port:
        warning("using port %s (instead of %s)", port, default_port)


# Backward-compatible alias (kept private) — used by legacy callers
# that monkeypatched the previous symbol name.
_parse_options = parse_args
