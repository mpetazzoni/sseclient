"""Parser benchmarks; normal pytest runs each case once without timing."""

import pytest

from sseclient import SSEClient


def parse(stream, chunk_size):
    # Construct a fresh source every invocation: generators are single-use.
    chunks = (stream[i : i + chunk_size] for i in range(0, len(stream), chunk_size))
    return list(SSEClient(chunks).events())


@pytest.mark.parametrize("size_mib", [1, 8])
@pytest.mark.parametrize("chunk_size", [128, 4096, 65536])
def test_large_single_line(benchmark, size_mib, chunk_size):
    payload = "A" * (size_mib * 1024 * 1024)
    stream = b"data: " + payload.encode() + b"\n\ndata: next\n\n"
    events = benchmark.pedantic(parse, args=(stream, chunk_size), rounds=3)
    assert [event.data for event in events] == [payload, "next"]


@pytest.mark.parametrize("line_size", [128, 1024])
def test_large_multiline(benchmark, line_size):
    lines = ["A" * line_size] * 8192
    stream = b"".join(b"data: " + line.encode() + b"\n" for line in lines) + b"\n"
    events = benchmark.pedantic(parse, args=(stream, 4096), rounds=3)
    assert len(events) == 1
    assert events[0].data == "\n".join(lines)


@pytest.mark.parametrize("chunk_size", [128, 4096])
def test_many_small_events(benchmark, chunk_size):
    stream = b"id: 1\nevent: update\ndata: hello\n\n" * 10000
    events = benchmark.pedantic(parse, args=(stream, chunk_size), rounds=3)
    assert len(events) == 10000
    assert all(
        (event.id, event.event, event.data) == ("1", "update", "hello")
        for event in events
    )


@pytest.mark.parametrize("chunk_size", [128, 4096])
def test_comments(benchmark, chunk_size):
    stream = b": keepalive\n\n" * 10000 + b"data: hello\n\n"
    events = benchmark.pedantic(parse, args=(stream, chunk_size), rounds=3)
    assert [event.data for event in events] == ["hello"]
