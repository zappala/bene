from __future__ import print_function

import sys

sys.path.append('..')

from src.sim import Sim
from src.packet import Packet

from networks.network import Network


class BroadcastApp(object):
    def __init__(self, node):
        self.node = node

    def receive_packet(self, packet):
        print(Sim.scheduler.current_time(), self.node.hostname, packet.ident)


def main():
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/five-nodes.txt')

    # get nodes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    n4 = net.get_node('n4')
    n5 = net.get_node('n5')

    # setup broadcast application
    b1 = BroadcastApp(n1)
    n1.add_protocol(protocol="broadcast", handler=b1)
    b2 = BroadcastApp(n2)
    n2.add_protocol(protocol="broadcast", handler=b2)
    b3 = BroadcastApp(n3)
    n3.add_protocol(protocol="broadcast", handler=b3)
    b4 = BroadcastApp(n4)
    n4.add_protocol(protocol="broadcast", handler=b4)
    b5 = BroadcastApp(n5)
    n5.add_protocol(protocol="broadcast", handler=b5)

    # send a broadcast packet from 1 with TTL 2, so everyone should get it
    p = Packet(
        source_address=n1.get_address('n2'),
        destination_address=0,
        ident=1, ttl=2, protocol='broadcast', length=100)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # send a broadcast packet from 1 with TTL 1, so just nodes 2 and 3
    # should get it
    p = Packet(
        source_address=n1.get_address('n2'),
        destination_address=0,
        ident=2, ttl=1, protocol='broadcast', length=100)
    Sim.scheduler.add(delay=1, event=p, handler=n1.send_packet)

    # send a broadcast packet from 3 with TTL 1, so just nodes 1, 4, and 5
    # should get it
    p = Packet(
        source_address=n3.get_address('n1'),
        destination_address=0,
        ident=3, ttl=1, protocol='broadcast', length=100)
    Sim.scheduler.add(delay=2, event=p, handler=n3.send_packet)

    # run the simulation
    Sim.scheduler.run()

if __name__ == '__main__':
    main()
