import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

class Generator(object):
    def __init__(self,node,duration):
        self.node = node
        self.start = 0
        self.duration = duration
        self.ident = 1

    def handle(self,event):
        # quit if done
        now = Sim.scheduler.current_time()
        if (now - self.start) > self.duration:
            return

        # generate a packet
        self.ident += 1
        p = packet.Packet(destination_address=2,ident=self.ident,protocol='delay',length=1000)
        self.node.handle_packet(p)
        Sim.scheduler.add(delay=0.1, event='generate', handler=self.handle)

class DelayHandler(object):
    def handle_packet(self,packet):
        print Sim.scheduler.current_time(),packet.ident,packet.created,Sim.scheduler.current_time() - packet.created,packet.queueing_delay

if __name__ == '__main__':
    Sim.scheduler.reset()
    # setup network
    n1 = node.Node()
    n2 = node.Node()
    l = link.Link(address=1,startpoint=n1,endpoint=n2)
    n1.add_link(l)
    n1.add_forwarding_entry(address=2,link=l)
    l = link.Link(address=2,startpoint=n2,endpoint=n1)
    n2.add_link(l)
    n2.add_forwarding_entry(address=1,link=l)
    d = DelayHandler()
    n2.add_protocol(protocol="delay",handler=d)
    # setup generator
    g = Generator(node=n1, duration=10)
    Sim.scheduler.add(delay=0, event='generate', handler=g.handle)
    Sim.scheduler.run()
