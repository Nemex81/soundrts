"""Round 13 - SOSPESO-A: documentazione tecnica via skipTest.

Conferma con un test esplicito che il sospeso WINDOWRESIZED/WINDOWSIZECHANGED
non è applicabile finché la Visual UI usa pygame.FULLSCREEN al posto di
pygame.RESIZABLE.
"""

import unittest


class WindowResizedSospesoTest(unittest.TestCase):
    def test_sospeso_a_skipped(self):
        self.skipTest(
            "SOSPESO-A scartato (Round 13): visual_mode=1 usa pygame.FULLSCREEN "
            "in soundrts/lib/screen.set_screen(); RESIZABLE non viene mai impostato, "
            "quindi un handler WINDOWRESIZED/WINDOWSIZECHANGED sarebbe codice morto. "
            "Riaprire il sospeso solo se viene introdotta una Visual UI windowed/resizable."
        )


if __name__ == "__main__":
    unittest.main()
