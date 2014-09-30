#!/usr/bin/env python3

"""A simple data type definition

It is just a simple data type for a host, with attributes for the hostname and
the ip address.

"""

import collections


#
# The data type for an internet host
# ----------------------------------
#

Host = collections.namedtuple(
    'Host',
    ['hostname',
     'ip']
    )
