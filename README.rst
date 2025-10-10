Server Side Events (SSE) client for Python
==========================================

A Python client for SSE event sources that seamlessly integrates with
``urllib3`` and ``requests``.

Installation
------------

.. code::

    $ pip install sseclient-py

Usage
-----

.. code:: python

    import json
    import pprint
    import sseclient

    def with_urllib3(url, headers):
        """Get a streaming response for the given event feed using urllib3."""
        import urllib3
        http = urllib3.PoolManager()
        yield from sseclient.SSEClient(http.request('GET', url, preload_content=False, headers=headers).events()

    def with_requests(url, headers):
        """Get a streaming response for the given event feed using requests."""
        import requests
        yield from sseclient.SSEClient(requests.get(url, stream=True, headers=headers)).events()

    def with_httpx(url, headers):
        """Get a streaming response for the given event feed using httpx."""
        import httpx
        with httpx.stream('GET', url, headers=headers) as s:
            # Note: 'yield from' is Python >= 3.3. Use for/yield instead if you
            # are using an earlier version.
            yield from sseclient.SSEClient(s.iter_bytes()).events()


    url = 'http://domain.com/events'
    headers = {'Accept': 'text/event-stream'}
    for event in with_urllib3(url, headers): # or with_requests(url, headers)
        pprint.pprint(json.loads(event.data))

Resources
=========

-  http://www.w3.org/TR/2009/WD-eventsource-20091029/
-  https://pypi.python.org/pypi/sseclient-py/
