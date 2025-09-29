"""Test file for pre-commit hooks."""

import os
import sys
from typing import List, Optional


def bad_function(param1: str, param2: Optional[str] = None) -> List[Optional[str]]:
    return [param1, param2]


class BadClass:
    def __init__(self, value: int) -> None:
        self.value = value

    def get_value(self) -> int:
        return self.value
