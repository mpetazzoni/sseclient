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

    import sseclient

    def with_urllib3(url):
        """Get a streaming response for the given event feed using urllib3."""
        import urllib3
        http = urllib3.PoolManager()
        res = http.request('GET', url, preload_content=False)
        yield from sseclient.SSEClient(res).events()

    def with_requests(url):
        """Get a streaming response for the given event feed using requests."""
        import requests
        res = requests.get(url, stream=True)
        yield from sseclient.SSEClient(res).events()

    def with_httpx(url):
        """Get a streaming response for the given event feed using httpx."""
        import httpx
        with httpx.stream('GET', url) as s:
            # Note: 'yield from' is Python >= 3.3. Use for/yield instead if you
            # are using an earlier version.
            yield from sseclient.SSEClient(s.iter_bytes()).events()


    url = 'http://domain.com/events'
    for event in with_urllib3(url):
        ...
    for event in with_requests(url):
        ...
    for event in with_httpx(url):
        ...

Resources
=========

-  http://www.w3.org/TR/2009/WD-eventsource-20091029/
-  https://pypi.python.org/pypi/sseclient-py/
