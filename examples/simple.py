import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

from networks.network import Network

import random

class DelayHandler(object):
    def receive_packet(self,packet):
        print Sim.scheduler.current_time(),packet.ident,packet.created,Sim.scheduler.current_time() - packet.created,packet.transmission_delay,packet.propagation_delay,packet.queueing_delay


if __name__ == '__main__':
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/one-hop.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

    # setup app
    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay",handler=d)

    # send one packet
    p = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # take the link down
    Sim.scheduler.add(delay=1, event=None, handler=n1.get_link('n2').down)

    # send one packet (it won't go through)
    p = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=1.1, event=p, handler=n1.send_packet)

    # bring the link up
    Sim.scheduler.add(delay=2, event=None, handler=n1.get_link('n2').up)

    # send one packet (and now it goes through)
    p = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=2.1, event=p, handler=n1.send_packet)


    # run the simulation
    Sim.scheduler.run()
