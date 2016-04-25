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


#peer = Peer(5)
#peer.start()

#time.sleep(30)
#print '~'*200
#peer.join()


import SocketServer

class MyUDPHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote:".format(self.client_address[0])
        print data
        socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    peer = Peer(5)
    peer.start()
    
    print '!'*200
    print 'Peer Server'
    
    HOST, PORT = "10.0.1.11", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()

