Server Side Events (SSE) client for Python
==========================================

A Python client for SSE event sources that seamlessly integrates with
``urllib3`` and ``requests``.

Usage
-----

.. code:: python

    import pprint
    import urllib3
    import sseclient

    http = urllib3.PoolManager()
    response = http.request('GET', 'http://domain.com/events')
    client = sseclient.SSEClient(response.stream())
    for event in client.events():
        pprint.pprint(json.loads(event.data))

Resources
=========

-  http://www.w3.org/TR/2009/WD-eventsource-20091029/
