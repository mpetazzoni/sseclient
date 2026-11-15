"""Benchmark fragmented single-line events; no timing assertions in CI.

Run: uv run python benchmarks/large_events.py --size-mib 8 --repeat 3
"""

import argparse
import platform
from statistics import median
from time import perf_counter

from sseclient import SSEClient


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size-mib", type=positive_int, default=8)
    parser.add_argument("--repeat", type=positive_int, default=3)
    parser.add_argument(
        "--chunk-sizes", type=positive_int, nargs="+", default=[128, 4096, 65536]
    )
    args = parser.parse_args()
    payload = "A" * (args.size_mib * 1024 * 1024)
    stream = b"data: " + payload.encode() + b"\n\ndata: next\n\n"
    print(f"Python {platform.python_version()}, {args.size_mib} MiB payload")
    for chunk_size in args.chunk_sizes:
        timings = []
        for _ in range(args.repeat):
            chunks = (
                stream[i : i + chunk_size] for i in range(0, len(stream), chunk_size)
            )
            start = perf_counter()
            events = list(SSEClient(chunks).events())
            timings.append(perf_counter() - start)
            assert [event.data for event in events] == [payload, "next"]
        seconds = median(timings)
        print(
            f"{chunk_size:>6} byte chunks: {seconds:.4f}s median, "
            f"{args.size_mib / seconds:.1f} MiB/s"
        )


if __name__ == "__main__":
    main()
