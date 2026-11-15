Server-Sent Events client for Python
====================================

``sseclient-py`` turns a streaming HTTP response into Server-Sent Events (SSE).
It works with ``requests``, ``urllib3`` and ``httpx``, and has no dependencies.
Python 3.11 or newer is required.

Installation
------------

.. code:: console

    $ pip install sseclient-py

Usage
-----

.. code:: python

    import requests
    import sseclient

    url = "https://example.com/events"
    with requests.get(
        url,
        headers={"Accept": "text/event-stream"},
        stream=True,
        timeout=(3.05, 60),
    ) as response:
        response.raise_for_status()
        for event in sseclient.SSEClient(response).events():
            print(event.id, event.event, event.data)

The timeout is a connect/read timeout, not a limit on the whole stream. Adjust
the read timeout to allow for your server's keep-alive interval.

Other HTTP clients
------------------

Pass the client's byte stream to ``SSEClient``:

.. code:: python

    import httpx
    import urllib3

    # urllib3
    http = urllib3.PoolManager()
    response = http.request("GET", url, preload_content=False)
    client = sseclient.SSEClient(response.stream())

    # httpx
    with httpx.stream("GET", url) as response:
        client = sseclient.SSEClient(response.iter_bytes())
        for event in client.events():
            print(event.data)

Reconnecting
------------

Connections and retries belong to the HTTP client. When ``events()`` returns,
connect again. To resume without repeating events, remember the last non-empty
``event.id`` and send it in the ``Last-Event-ID`` header on the new request.
Use a delay or backoff between attempts.

The yielded events have ``id``, ``event``, ``data`` and ``retry`` attributes.
Comments and events without data are ignored.

Resources
---------

- `SSE specification <https://html.spec.whatwg.org/multipage/server-sent-events.html>`_
- `PyPI <https://pypi.org/project/sseclient-py/>`_
- `Source and issues <https://github.com/mpetazzoni/sseclient>`_
