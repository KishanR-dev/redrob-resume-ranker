from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Generator

from .models import CandidateRecord


def iter_candidates(path: str) -> Generator[CandidateRecord, None, None]:
    p = Path(path)
    opener = gzip.open if p.suffix == ".gz" else open

    with opener(p, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
