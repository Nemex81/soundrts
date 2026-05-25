"""Round 14 - TASK-2: verifica fallback silenzioso del version check.

L'endpoint http://jlpo.free.fr/soundrts/<major.minor>version.txt potrebbe
non esistere per i rami nuovi (es. 1.4version.txt restituisce HTTP 404).
Il codice in soundrts.clientversion.RevisionChecker.run() deve gestire
qualsiasi errore di rete senza propagare eccezioni e senza emettere TTS,
garantendo l'invariante audio-only (LEGGE-1) e la backward compatibility
(LEGGE-3).
"""

import unittest
import urllib.error
from unittest.mock import patch

from soundrts import clientversion


class VersionCheckFallbackTest(unittest.TestCase):
    def test_http_404_does_not_raise(self):
        """RevisionChecker.run() ignora silenziosamente un HTTP 404."""
        err = urllib.error.HTTPError(
            "http://jlpo.free.fr/soundrts/1.4version.txt",
            404,
            "Not Found",
            hdrs=None,  # type: ignore[arg-type]
            fp=None,
        )
        checker = clientversion.RevisionChecker()
        with patch("urllib.request.urlopen", side_effect=err), patch(
            "soundrts.clientversion.stats.Stats"
        ), patch("soundrts.clientversion.update_packages_from_servers"):
            checker.run()

    def test_network_timeout_does_not_raise(self):
        """RevisionChecker.run() ignora silenziosamente un timeout di rete."""
        checker = clientversion.RevisionChecker()
        with patch(
            "urllib.request.urlopen", side_effect=TimeoutError("timed out")
        ), patch("soundrts.clientversion.stats.Stats"), patch(
            "soundrts.clientversion.update_packages_from_servers"
        ):
            checker.run()

    def test_url_error_does_not_raise(self):
        """RevisionChecker.run() ignora silenziosamente un URLError generico."""
        checker = clientversion.RevisionChecker()
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("unreachable"),
        ), patch("soundrts.clientversion.stats.Stats"), patch(
            "soundrts.clientversion.update_packages_from_servers"
        ):
            checker.run()


if __name__ == "__main__":
    unittest.main()
