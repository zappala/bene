import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

import random

class BroadcastApp(object):
    def __init__(self,node):
        self.node = node

    def receive_packet(self,packet):
        print Sim.scheduler.current_time(),self.node.hostname,packet.ident

if __name__ == '__main__':
    # parameters
    Sim.scheduler.reset()
    Sim.set_debug(True)

    # setup network
    n1 = node.Node('n1')
    n2 = node.Node('n2')
    n3 = node.Node('n3')
    n4 = node.Node('n4')
    n5 = node.Node('n5')
    # link from 1 to 2
    l = link.Link(address=1,startpoint=n1,endpoint=n2)
    n1.add_link(l)
    # link from 2 to 1
    l = link.Link(address=2,startpoint=n2,endpoint=n1)
    n2.add_link(l)
    # link from 1 to 3
    l = link.Link(address=3,startpoint=n1,endpoint=n3)
    n1.add_link(l)
    # link from 3 to 1
    l = link.Link(address=4,startpoint=n3,endpoint=n1)
    n3.add_link(l)
    # link from 3 to 4
    l = link.Link(address=5,startpoint=n3,endpoint=n4)
    n3.add_link(l)
    # link from 4 to 3
    l = link.Link(address=6,startpoint=n4,endpoint=n3)
    n4.add_link(l)
    # link from 3 to 5
    l = link.Link(address=7,startpoint=n3,endpoint=n5)
    n3.add_link(l)
    # link from 5 to 3
    l = link.Link(address=8,startpoint=n5,endpoint=n3)
    n5.add_link(l)

    # setup broadcast application
    b1 = BroadcastApp(n1)
    n1.add_protocol(protocol="broadcast",handler=b1)
    b2 = BroadcastApp(n2)
    n2.add_protocol(protocol="broadcast",handler=b2)
    b3 = BroadcastApp(n3)
    n3.add_protocol(protocol="broadcast",handler=b3)
    b4 = BroadcastApp(n4)
    n4.add_protocol(protocol="broadcast",handler=b4)
    b5 = BroadcastApp(n5)
    n5.add_protocol(protocol="broadcast",handler=b5)

    # send a broadcast packet from 1 with TTL 2, so everyone should get it
    p = packet.Packet(source_address=1,destination_address=0,ident=1,ttl=2,protocol='broadcast',length=100)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # send a broadcast packet from 1 with TTL 1, so just nodes 2 and 3
    # should get it
    p = packet.Packet(source_address=1,destination_address=0,ident=2,ttl=1,protocol='broadcast',length=100)
    Sim.scheduler.add(delay=1, event=p, handler=n1.send_packet)

    # send a broadcast packet from 3 with TTL 1, so just nodes 1, 4, and 5
    # should get it
    p = packet.Packet(source_address=4,destination_address=0,ident=3,ttl=1,protocol='broadcast',length=100)
    Sim.scheduler.add(delay=2, event=p, handler=n3.send_packet)

    # run the simulation
    Sim.scheduler.run()
