# Copyright (C) 2016 SignalFx, Inc. All rights reserved.

_FIELD_SEPARATOR = ':'


class SSEClient(object):
    """Implementation of a SSE client.

    See http://www.w3.org/TR/2009/WD-eventsource-20091029/ for the
    specification.
    """

    def __init__(self, stream):
        """Initialize the SSE client over an existing, ready to consume
        response stream."""
        self._stream = stream

    def events(self):
        for chunk in self._stream:
            event = {}
            for line in chunk.splitlines():
                # Lines starting with a separator are to be ignored.
                if not line.strip() or line.startswith(_FIELD_SEPARATOR):
                    continue

                data = line.split(_FIELD_SEPARATOR, 1)
                field = data[0]

                # Spaces may occur before the value; strip them. If no value is
                # present after the separator, assume an empty value.
                value = data[1].lstrip() if len(data) > 1 else ''

                # The data field may come over multiple lines and their values
                # are concatenated with each other.
                if field == 'data' and field in event:
                    event[field] += value
                else:
                    event[field] = value

            # Events with no data are not dispatched.
            if 'data' not in event or not event['data']:
                continue

            # If the data field ends with a newline, remove it.
            if event['data'].endswith('\n'):
                event['data'] = event['data'][0:-1]

            # Dispatch the event
            yield Event(**event)


class Event(object):
    """Representation of an event from the event stream."""

    def __init__(self, id=None, event='message', data='', retry=None):
        self._id = id
        self._event = event
        self._data = data
        self._retry = retry

    @property
    def id(self):
        return self._id

    @property
    def event(self):
        return self._event

    @property
    def data(self):
        return self._data

    @property
    def retry(self):
        return self._data
