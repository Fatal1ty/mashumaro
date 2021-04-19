from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mashumaro import DataClassDictMixin


@dataclass
class Node(DataClassDictMixin):
    next: Optional[Node] = None
