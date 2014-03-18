from sim import Sim

class Transport(object):
    def __init__(self,node):
        self.node = node
        self.binding = {}
        self.node.add_protocol(protocol="TCP",handler=self)

    def bind(self,connection,source_address,source_port,
             destination_address,destination_port):
        # setup binding so that packets we receive for this combination
        # are sent to the right socket
        tuple = (destination_address,destination_port,
                 source_address,source_port)
        self.binding[tuple] = connection

    def receive_packet(self,packet):
        tuple = (packet.source_address,packet.source_port,
                 packet.destination_address,packet.destination_port)
        self.binding[tuple].receive_packet(packet)

    def send_packet(self,packet):
        Sim.scheduler.add(delay=0, event=packet, handler=self.node.send_packet)
