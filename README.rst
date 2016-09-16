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

    def with_urllib3(url):
        """Get a streaming response for the given event feed using urllib3."""
        import urllib3
        http = urllib3.PoolManager()
        return http.request('GET', url, preload_content=False)

    def with_requests(url):
        """Get a streaming response for the given event feed using requests."""
        import requests
        return requests.get(url, stream=True)

    url = 'http://domain.com/events'
    response = with_urllib3(url)  # or with_requests(url)
    client = sseclient.SSEClient(response)
    for event in client.events():
        pprint.pprint(json.loads(event.data))

Resources
=========

-  http://www.w3.org/TR/2009/WD-eventsource-20091029/
-  https://pypi.python.org/pypi/sseclient-py/
