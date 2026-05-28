"""Quick coverage check for Task 1: verify all tts.txt files contain
SET_SPEED_1..7 + PAUSE_ON/OFF (IDs 4367-4375).
"""
from pathlib import Path
import re

ids = [4367, 4368, 4369, 4370, 4371, 4372, 4373, 4374, 4375]
files = [Path("res/ui/tts.txt")] + sorted(Path("res").glob("ui-*/tts.txt"))
missing = 0
for p in files:
    text = p.read_text(encoding="utf-8", errors="replace")
    for i in ids:
        if not re.search(rf"(?m)^{i}\s", text):
            print(f"MISSING {p} -> {i}")
            missing += 1
if missing == 0:
    print(f"OK: tutti gli ID 4367-4375 presenti in {len(files)} file tts.txt")
else:
    print(f"FAIL: {missing} entry mancanti")
