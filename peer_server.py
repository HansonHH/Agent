#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""
from cyclon.peer import Peer
import time

print '!'*200
print 'Peer Server'

peer = Peer(5)
peer.start()

#time.sleep(30)
print '~'*200
#peer.join()


