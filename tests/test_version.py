"""The frontend file is cached by its versioned URL, so every version number must change together."""

import json
import re
from pathlib import Path

from custom_components.connect_four.const import VERSION

ROOT = Path(__file__).parent.parent / "custom_components" / "connect_four"


def test_versions_match():
    assert json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["version"] == VERSION
    js = (ROOT / "frontend" / "connect-four.js").read_text(encoding="utf-8")
    assert re.search(r'CF_VERSION = "([^"]+)"', js).group(1) == VERSION
