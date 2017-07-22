# coding: utf-8
"""
Tests mosly copied from:

https://github.com/EventSource/eventsource/blob/master/test/eventsource_test.js
"""

import os
import sys
import struct
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sseclient

def parse(content):
    return [{ 'id': ev.id,
              'event': ev.event,
              'data': ev.data }
            for ev in sseclient.SSEClient(content).events()]

class Parser(unittest.TestCase):
    def test_multibyte_characters(self):
        self.assertEqual(parse([u'id: 1\ndata: €豆腐\n\n'.encode('utf-8')]),
        [{
            'id': '1',
            'event': 'message',
            'data': u'€豆腐'
        }])

    def test_parses_empty_lines_with_multibyte_characters(self):
        self.assertEqual(parse([u'\n\n\n\nid: 1\ndata: 我現在都看實況不玩遊戲\n\n'.encode('utf-8')]),
        [{
            'id': '1',
            'event': 'message',
            'data': u'我現在都看實況不玩遊戲'
        }])

    def test_one_one_line_message_in_one_chunk(self):
        self.assertEqual(parse([b'data: Hello\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'Hello'
        }])

    def test_one_one_line_message_in_two_chunks(self):
        self.assertEqual(parse([b'data: Hel', b'lo\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'Hello'
        }])

    def test_two_one_line_messages_in_one_chunk(self):
        self.assertEqual(parse([b'data: Hello\n\n', b'data: World\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'Hello'
        }, {
            'id': None,
            'event': 'message',
            'data': 'World'
        }])

    def test_one_two_line_message_in_one_chunk(self):
        self.assertEqual(parse([b'data: Hello\ndata:World\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'Hello\nWorld'
        }])

    # Issue #8
    def test_really_chopped_up_unicode_data(self):
        self.assertEqual(parse([struct.pack('B', b) for b in bytearray(u'data: Aslak\n\ndata: Hellesøy\n\n'.encode('utf-8'))]),
        [{
            'id': None,
            'event': 'message',
            'data': 'Aslak'
        }, {
            'id': None,
            'event': 'message',
            'data': u'Hellesøy'
        }])

    def test_accepts_CRLF_as_separator(self):
        self.assertEqual(parse([struct.pack('B', b) for b in bytearray(u'data: Aslak\r\n\r\ndata: Hellesøy\r\n\r\n'.encode('utf-8'))]),
        [{
            'id': None,
            'event': 'message',
            'data': 'Aslak'
        }, {
            'id': None,
            'event': 'message',
            'data': u'Hellesøy'
        }])

    def test_accepts_CR_as_separator(self):
        self.assertEqual(parse([struct.pack('B', b) for b in bytearray(u'data: Aslak\r\rdata: Hellesøy\r\r'.encode('utf-8'))]),
        [{
            'id': None,
            'event': 'message',
            'data': 'Aslak'
        }, {
            'id': None,
            'event': 'message',
            'data': u'Hellesøy'
        }])

    def test_delivers_message_with_explicit_event(self):
        self.assertEqual(parse([b'event: greeting\ndata: Hello\n\n']),
        [{
            'id': None,
            'event': 'greeting',
            'data': 'Hello'
        }])

    def test_delivers_two_messages_with_same_explicit_event(self):
        self.assertEqual(parse([b'event: greeting\ndata: Hello\n\n', b'event: greeting\ndata: World\n\n']),
        [{
            'id': None,
            'event': 'greeting',
            'data': 'Hello'
        },
        {
            'id': None,
            'event': 'greeting',
            'data': 'World'
        }])

    def test_delivers_two_messages_with_different_explicit_events(self):
        self.assertEqual(parse([b'event: greeting\ndata: Hello\n\n', b'event: salutation\ndata: World\n\n']),
        [{
            'id': None,
            'event': 'greeting',
            'data': 'Hello'
        },
        {
            'id': None,
            'event': 'salutation',
            'data': 'World'
        }])

    def test_ignores_comments(self):
        self.assertEqual(parse([b'data: Hello\n\n:nothing to see here\n\ndata: World\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'Hello'
        },
        {
            'id': None,
            'event': 'message',
            'data': 'World'
        }])
       
    def test_ignores_empty_comments(self):
        self.assertEqual(parse([b'data: Hello\n\n:\n\ndata: World\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'Hello'
        },
        {
            'id': None,
            'event': 'message',
            'data': 'World'
        }])
 
    def test_does_not_ignore_multiline_strings(self):
        self.assertEqual(parse([b'data: line one\ndata:\ndata: line two\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'line one\n\nline two'
        }])

    def test_does_not_ignore_multiline_strings_even_in_data_beginning(self):
        self.assertEqual(parse([b'data:\ndata:line one\ndata: line two\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': '\nline one\nline two'
        }])

    def test_should_regard_empty_event_as_message(self):
        self.assertEqual(parse([b'event:\ndata: Hello\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'Hello'
        }])

    def test_should_ignore_message_with_no_data(self):
        self.assertEqual(parse([b'event: greeting\n\n']), [])

    def test_preserves_whitespace_at_end_of_lines(self):
        self.assertEqual(parse([b'event: greeting \ndata: Hello  \n\n']),
        [{
            'id': None,
            'event': 'greeting ',
            'data': 'Hello  '
        }])

    def test_parses_relatively_huge_messages_efficiently(self):
        self.assertEqual(parse([b'data: ' + b'a'*10000 + b'\n\n']),
        [{
            'id': None,
            'event': 'message',
            'data': 'a'*10000
        }])

    def test_ID(self):
        self.assertEqual(parse([b'id: 90\ndata: Hello\n\n']),
        [{
            'id': '90',
            'event': 'message',
            'data': 'Hello'
        }])

    # Issue #9
    def test_does_not_split_on_universal_newlines(self):
        self.assertEqual(parse([u'data: Hello\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029\n\n'.encode('utf-8')]),
        [{
            'id': None,
            'event': 'message',
            'data': u'Hello\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029'
        }])

    # Issue #11 and PR #12
    def test_empty_line_at_start_of_chunk(self):
        self.assertEqual(parse([
            b'event: test event\r\ndata: {\r\ndata:     "terribly_split": "json_objects in SSE",',
            b'\r\ndata:     "which_should_probably": "be on a single line",\r\ndata:     "but_oh_well": 1\r\ndata: }\r\n\r\n']),
        [{
            'id': None,
            'event': 'test event',
            # From the spec https://www.w3.org/TR/2009/WD-eventsource-20091029/
            # "If the field name is "data"
            #  Append the field value to the data buffer, then append a single
            #  U+000A LINE FEED (LF) character to the data buffer."
            # So the lines should be separated by \n
            'data': '{\n    "terribly_split": "json_objects in SSE",\n    "which_should_probably": "be on a single line",\n    "but_oh_well": 1\n}'
        }])

if __name__ == '__main__':
    unittest.main()
