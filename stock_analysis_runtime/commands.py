"""Pure command parser for the canonical conversation progression contract."""

from __future__ import annotations

from enum import StrEnum


class Command(StrEnum):
    NEXT = "next"
    UPDATE = "update"
    NONE = "none"


def parse_command(message: str, *, initial_complete: bool) -> Command:
    """Recognize only exact commands; questions and embedded text never advance."""
    if message == "次":
        return Command.NEXT
    if message == "更新" and initial_complete:
        return Command.UPDATE
    return Command.NONE
