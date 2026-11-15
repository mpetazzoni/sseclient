# Parser benchmarks

Normal `uv run pytest` runs these cases once for correctness, without timing. CI uses the same default; no wall-clock thresholds.

Measure performance locally:

```sh
uv run pytest tests/benchmarks --benchmark-only --benchmark-enable
```

Save a baseline, then compare another checkout on the same machine and Python version:

```sh
uv run pytest tests/benchmarks --benchmark-only --benchmark-enable --benchmark-save=before
uv run pytest tests/benchmarks --benchmark-only --benchmark-enable --benchmark-compare
```

Cases cover single-line and multiline payloads, small events, and comments. Payload construction and correctness assertions are outside the timed call; each call creates a fresh byte iterator. Each benchmark uses three rounds.
