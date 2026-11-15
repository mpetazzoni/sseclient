"""Check the public stub against the minimum supported Python version."""

from collections.abc import Generator, Iterable, Iterator

from sseclient import Event, SSEClient


class Response:
    """A response can be iterable without being an iterator itself."""

    def __iter__(self) -> Iterator[bytes]:
        return iter([b"data: hello\n\n"])


def events(source: Iterable[bytes]) -> Generator[Event, None, None]:
    return SSEClient(source).events()


list_events = events([b"data: hello\n\n"])
iterator_events = events(iter([b"data: hello\n\n"]))
response_events = events(Response())
