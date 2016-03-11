"""
Server Side Events (SSE) client for Python.

Provides a generator of SSE received through an existing HTTP response.
"""

# Copyright (C) 2016 SignalFx, Inc. All rights reserved.

import client


__author__ = 'Maxime Petazzoni <maxime.petazzoni@bulix.org>'
__email__ = 'maxime.petazzoni@bulix.org'
__copyright__ = 'Copyright (C) 2016 SignalFx, Inc. All rights reserved.'
__all__ = ['SSEClient']

SSEClient = client.SSEClient
