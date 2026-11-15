"""
Unit tests for SSEClient. Tests were mostly copied from:
https://github.com/EventSource/eventsource/blob/master/test/eventsource_test.js
"""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sseclient


def parse(content):
    return [
        {"id": ev.id, "event": ev.event, "data": ev.data}
        for ev in sseclient.SSEClient(content).events()
    ]


class Parser(unittest.TestCase):
    def test_ignores_initial_bom(self):
        content = "\ufeffdata: Hello\n\n".encode("utf-8")
        for chunks in ([content], [content[:1], content[1:2], content[2:]]):
            with self.subTest(chunks=chunks):
                self.assertEqual(
                    parse(chunks),
                    [{"id": None, "event": "message", "data": "Hello"}],
                )

    def test_initial_bom_before_id(self):
        self.assertEqual(
            parse(["\ufeffid: 1\ndata: Hello\n\n".encode("utf-8")]),
            [{"id": "1", "event": "message", "data": "Hello"}],
        )

    def test_preserves_bom_in_later_event_data(self):
        self.assertEqual(
            parse(["data: first\n\ndata: \ufeffsecond\n\n".encode("utf-8")]),
            [
                {"id": None, "event": "message", "data": "first"},
                {"id": None, "event": "message", "data": "\ufeffsecond"},
            ],
        )

    def test_only_one_initial_bom_is_ignored(self):
        self.assertEqual(
            parse(["\ufeff\ufeffdata: ignored\ndata: Hello\n\n".encode("utf-8")]),
            [{"id": None, "event": "message", "data": "Hello"}],
        )

    def test_bom_after_initial_newline_is_not_ignored(self):
        self.assertEqual(parse(["\n\ufeffdata: ignored\n\n".encode("utf-8")]), [])

    def test_multibyte_characters(self):
        self.assertEqual(
            parse(["id: 1\ndata: €豆腐\n\n".encode()]),
            [{"id": "1", "event": "message", "data": "€豆腐"}],
        )

    def test_parses_empty_lines_with_multibyte_characters(self):
        self.assertEqual(
            parse(["\n\n\n\nid: 1\ndata: 我現在都看實況不玩遊戲\n\n".encode()]),
            [{"id": "1", "event": "message", "data": "我現在都看實況不玩遊戲"}],
        )

    def test_one_one_line_message_in_one_chunk(self):
        self.assertEqual(
            parse([b"data: Hello\n\n"]),
            [{"id": None, "event": "message", "data": "Hello"}],
        )

    def test_one_one_line_message_in_two_chunks(self):
        self.assertEqual(
            parse([b"data: Hel", b"lo\n\n"]),
            [{"id": None, "event": "message", "data": "Hello"}],
        )

    def test_two_one_line_messages_in_one_chunk(self):
        self.assertEqual(
            parse([b"data: Hello\n\n", b"data: World\n\n"]),
            [
                {"id": None, "event": "message", "data": "Hello"},
                {"id": None, "event": "message", "data": "World"},
            ],
        )

    def test_one_two_line_message_in_one_chunk(self):
        self.assertEqual(
            parse([b"data: Hello\ndata:World\n\n"]),
            [{"id": None, "event": "message", "data": "Hello\nWorld"}],
        )

    # Issue #8
    def test_really_chopped_up_unicode_data(self):
        self.assertEqual(
            parse(
                [
                    struct.pack("B", b)
                    for b in bytearray("data: Aslak\n\ndata: Hellesøy\n\n".encode())
                ]
            ),
            [
                {"id": None, "event": "message", "data": "Aslak"},
                {"id": None, "event": "message", "data": "Hellesøy"},
            ],
        )

    def test_accepts_CRLF_as_separator(self):
        self.assertEqual(
            parse(
                [
                    struct.pack("B", b)
                    for b in bytearray(
                        "data: Aslak\r\n\r\ndata: Hellesøy\r\n\r\n".encode()
                    )
                ]
            ),
            [
                {"id": None, "event": "message", "data": "Aslak"},
                {"id": None, "event": "message", "data": "Hellesøy"},
            ],
        )

    def test_accepts_CR_as_separator(self):
        self.assertEqual(
            parse(
                [
                    struct.pack("B", b)
                    for b in bytearray("data: Aslak\r\rdata: Hellesøy\r\r".encode())
                ]
            ),
            [
                {"id": None, "event": "message", "data": "Aslak"},
                {"id": None, "event": "message", "data": "Hellesøy"},
            ],
        )

    def test_mixed_line_endings_across_chunk_boundaries(self):
        endings = (b"\r", b"\n", b"\r\n")
        expected = [
            {"id": "1", "event": "greeting", "data": "first"},
            {"id": "2", "event": "message", "data": "second"},
        ]
        for first in endings:
            for second in endings:
                if first + second == b"\r\n":
                    continue
                content = (
                    b"id: 1\nevent: greeting\ndata: first"
                    + first
                    + second
                    + b"id: 2\ndata: second\n\n"
                )
                for boundary in range(len(content) + 1):
                    with self.subTest(first=first, second=second, boundary=boundary):
                        self.assertEqual(
                            parse([content[:boundary], content[boundary:]]), expected
                        )
                with self.subTest(first=first, second=second, chunking="bytes"):
                    self.assertEqual(
                        parse([content[i : i + 1] for i in range(len(content))]),
                        expected,
                    )

    def test_split_CRLF_with_empty_chunks_is_one_line_ending(self):
        self.assertEqual(
            parse([b"data: first\r", b"", b"\n", b"", b"data: second\n\n"]),
            [{"id": None, "event": "message", "data": "first\nsecond"}],
        )

    def test_mixed_line_endings_dispatch_before_next_chunk(self):
        def source():
            yield b"data: first\r\n\r"
            self.fail("The next chunk was read before dispatching the event")

        self.assertEqual(next(sseclient.SSEClient(source()).events()).data, "first")

    def test_final_partial_event_with_mixed_line_endings(self):
        self.assertEqual(
            parse([b"data: first\r\n\r", b"\ndata: second"]),
            [
                {"id": None, "event": "message", "data": "first"},
                {"id": None, "event": "message", "data": "second"},
            ],
        )

    def test_delivers_message_with_explicit_event(self):
        self.assertEqual(
            parse([b"event: greeting\ndata: Hello\n\n"]),
            [{"id": None, "event": "greeting", "data": "Hello"}],
        )

    def test_delivers_two_messages_with_same_explicit_event(self):
        self.assertEqual(
            parse(
                [
                    b"event: greeting\ndata: Hello\n\n",
                    b"event: greeting\ndata: World\n\n",
                ]
            ),
            [
                {"id": None, "event": "greeting", "data": "Hello"},
                {"id": None, "event": "greeting", "data": "World"},
            ],
        )

    def test_delivers_two_messages_with_different_explicit_events(self):
        self.assertEqual(
            parse(
                [
                    b"event: greeting\ndata: Hello\n\n",
                    b"event: salutation\ndata: World\n\n",
                ]
            ),
            [
                {"id": None, "event": "greeting", "data": "Hello"},
                {"id": None, "event": "salutation", "data": "World"},
            ],
        )

    def test_ignores_comments(self):
        self.assertEqual(
            parse([(b"data: Hello\n\n:nothing to see here\n\ndata: World\n\n")]),
            [
                {"id": None, "event": "message", "data": "Hello"},
                {"id": None, "event": "message", "data": "World"},
            ],
        )

    def test_ignores_empty_comments(self):
        self.assertEqual(
            parse([b"data: Hello\n\n:\n\ndata: World\n\n"]),
            [
                {"id": None, "event": "message", "data": "Hello"},
                {"id": None, "event": "message", "data": "World"},
            ],
        )

    def test_does_not_ignore_multiline_strings(self):
        self.assertEqual(
            parse([b"data: line one\ndata:\ndata: line two\n\n"]),
            [{"id": None, "event": "message", "data": "line one\n\nline two"}],
        )

    def test_does_not_ignore_multiline_strings_even_in_data_beginning(self):
        self.assertEqual(
            parse([b"data:\ndata:line one\ndata: line two\n\n"]),
            [{"id": None, "event": "message", "data": "\nline one\nline two"}],
        )

    def test_should_regard_empty_event_as_message(self):
        self.assertEqual(
            parse([b"event:\ndata: Hello\n\n"]),
            [{"id": None, "event": "message", "data": "Hello"}],
        )

    def test_should_ignore_message_with_no_data(self):
        self.assertEqual(parse([b"event: greeting\n\n"]), [])

    def test_preserves_whitespace_at_end_of_lines(self):
        self.assertEqual(
            parse([b"event: greeting \ndata: Hello  \n\n"]),
            [{"id": None, "event": "greeting ", "data": "Hello  "}],
        )

    def test_parses_relatively_huge_messages_efficiently(self):
        self.assertEqual(
            parse([b"data: " + b"a" * 10000 + b"\n\n"]),
            [{"id": None, "event": "message", "data": "a" * 10000}],
        )

    def test_large_fragmented_events(self):
        payload = "A" * (2 * 1024 * 1024)
        for ending in (b"\n", b"\r", b"\r\n"):
            stream = (
                b"id: large"
                + ending
                + b"data: "
                + payload.encode()
                + ending * 2
                + b"data: next"
                + ending * 2
            )
            for chunk_size in (128, 4096, 65536):
                with self.subTest(ending=ending, chunk_size=chunk_size):
                    chunks = (
                        stream[i : i + chunk_size]
                        for i in range(0, len(stream), chunk_size)
                    )
                    self.assertEqual(
                        parse(chunks),
                        [
                            {"id": "large", "event": "message", "data": payload},
                            {"id": None, "event": "message", "data": "next"},
                        ],
                    )

    def test_read_yields_independent_bytes(self):
        reader = sseclient.SSEClient([b"data: first\n\ndata: second\n\n"])._read()
        first = next(reader)
        second = next(reader)
        self.assertIs(type(first), bytes)
        self.assertIs(type(second), bytes)
        self.assertEqual(first, b"data: first\n\n")
        self.assertEqual(second, b"data: second\n\n")
        self.assertEqual(list(reader), [])
        self.assertEqual(first, b"data: first\n\n")

    def test_large_fragmented_partial_event_at_eof(self):
        payload = "A" * (2 * 1024 * 1024)
        stream = b"data: " + payload.encode()
        chunks = (stream[i : i + 128] for i in range(0, len(stream), 128))
        self.assertEqual(
            parse(chunks), [{"id": None, "event": "message", "data": payload}]
        )

    def test_read_partial_event_yields_bytes(self):
        chunks = list(sseclient.SSEClient([b"data: par", b"tial"])._read())
        self.assertEqual(chunks, [b"data: partial"])
        self.assertIs(type(chunks[0]), bytes)

    def test_large_multiline_event(self):
        lines = [" €豆腐 " * 32] * 8192
        stream = (
            "id: large\nevent: update\nretry: 1000\n"
            + "".join("data: " + line + "\n" for line in lines)
            + "\ndata: next\n\n"
        ).encode()
        chunks = (stream[i : i + 128] for i in range(0, len(stream), 128))
        events = list(sseclient.SSEClient(chunks).events())
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].data, "\n".join(lines))
        self.assertEqual(events[0].id, "large")
        self.assertEqual(events[0].event, "update")
        self.assertEqual(events[0].retry, "1000")
        self.assertEqual(events[1].data, "next")

    def test_empty_data_field_still_dispatches(self):
        self.assertEqual(
            parse([b"id: ignored\n\ndata:\n\ndata:\ndata:\n\n"]),
            [
                {"id": None, "event": "message", "data": ""},
                {"id": None, "event": "message", "data": "\n"},
            ],
        )

    def test_ID(self):
        self.assertEqual(
            parse([b"id: 90\ndata: Hello\n\n"]),
            [{"id": "90", "event": "message", "data": "Hello"}],
        )

    # Issue #9
    def test_does_not_split_on_universal_newlines(self):
        self.assertEqual(
            parse(
                ["data: Hello\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029\n\n".encode("utf-8")]
            ),
            [
                {
                    "id": None,
                    "event": "message",
                    "data": "Hello\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029",
                }
            ],
        )

    # Issue #11 and PR #12
    def test_empty_line_at_start_of_chunk(self):
        self.assertEqual(
            parse(
                [
                    (
                        b"event: test event\r\ndata: {\r\ndata:"
                        b'     "terribly_split": "json_objects in SSE",'
                    ),
                    (
                        b'\r\ndata:     "which_should_probably": '
                        b'"be on a single line",\r\ndata:'
                        b'     "but_oh_well": 1\r\ndata: }\r\n\r\n'
                    ),
                ]
            ),
            # From the spec
            # https://www.w3.org/TR/2009/WD-eventsource-20091029/ "If the
            # field name is "data" Append the field value to the data
            # buffer, then append a single U+000A LINE FEED (LF) character
            # to the data buffer." So the lines should be separated by \n
            [
                {
                    "id": None,
                    "event": "test event",
                    "data": (
                        '{\n    "terribly_split": "json_objects in SSE",\n'
                        '    "which_should_probably": "be on a single line",\n'
                        '    "but_oh_well": 1\n}'
                    ),
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
