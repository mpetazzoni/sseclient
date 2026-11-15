"""
Server Side Events (SSE) client for Python.

Provides a generator of SSE received through an existing HTTP response.
"""

from collections.abc import Generator, Iterator
from typing import Any

__all__ = ["SSEClient"]

class SSEClient:
    """SSE client interface."""

    def __init__(self, event_source: Iterator[bytes], char_enc: str = "utf-8"): ...
    def events(self) -> Generator[Event]: ...
    def close(self) -> None: ...

class Event:
    """Representation of an event from the event stream."""

    id: str | None
    event: str
    data: str
    retry: Any | None
