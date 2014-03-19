import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

import random

class DelayHandler(object):
    def receive_packet(self,packet):
        print Sim.scheduler.current_time(),packet.ident,packet.created,Sim.scheduler.current_time() - packet.created,packet.transmission_delay,packet.propagation_delay,packet.queueing_delay



if __name__ == '__main__':
    # parameters
    Sim.scheduler.reset()

    # setup network
    n1 = node.Node('n1')
    n2 = node.Node('n2')
    l = link.Link(address=1,startpoint=n1,endpoint=n2)
    n1.add_link(l)
    n1.add_forwarding_entry(address=2,link=l)
    l = link.Link(address=2,startpoint=n2,endpoint=n1)
    n2.add_link(l)
    n2.add_forwarding_entry(address=1,link=l)
    d = DelayHandler()
    n2.add_protocol(protocol="delay",handler=d)

    # send one packet
    p = packet.Packet(destination_address=2,ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # take the link down
    Sim.scheduler.add(delay=1, event=None, handler=n1.links[0].down)

    # send one packet (it won't go through)
    p = packet.Packet(destination_address=2,ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=1.1, event=p, handler=n1.send_packet)

    # bring the link up
    Sim.scheduler.add(delay=2, event=None, handler=n1.links[0].up)

    # send one packet (and now it goes through)
    p = packet.Packet(destination_address=2,ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=2.1, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()
