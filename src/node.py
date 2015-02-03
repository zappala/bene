from sim import Sim

import copy

class Node(object):
    def __init__(self,hostname):
        self.hostname = hostname
        self.links = []
        self.protocols = {}
        self.forwarding_table = {}

    def trace(self,message):
        Sim.trace("Node",message)

    ## Links ## 

    def add_link(self,link):
        self.links.append(link)

    def delete_link(self,link):
        if link not in self.links:
            return
        self.links.remove(link)

    def get_link(self,name):
        for link in self.links:
            if link.endpoint.hostname == name:
                return link
        return None

    def get_address(self,name):
        for link in self.links:
            if link.endpoint.hostname == name:
                return link.address
        return 0

    ## Protocols ## 

    def add_protocol(self,protocol,handler):
        self.protocols[protocol] = handler

    def delete_protocol(self,protocol):
        if protocol not in self.protocols:
            return
        del self.protocols[protocol]

    ## Forwarding table ##

    def add_forwarding_entry(self,address,link):
        self.forwarding_table[address] = link

    def delete_forwarding_entry(self,address,link):
        if address not in self.forwarding_table:
            return
        del self.forwarding_table[address]

    ## Handling packets ##

    def send_packet(self,packet):
        # if this is the first time we have seen this packet, set its
        # creation timestamp
        if packet.created == None:
            packet.created = Sim.scheduler.current_time()

        # forward the packet
        self.forward_packet(packet)

    def receive_packet(self,packet):
        # handle broadcast packets
        if packet.destination_address == 0:
            self.trace("%s received packet" % (self.hostname))
            self.deliver_packet(packet)
        else:
            # check if unicast packet is for me
            for link in self.links:
                if link.address == packet.destination_address:
                    self.trace("%s received packet" % (self.hostname))
                    self.deliver_packet(packet)
                    return

        # decrement the TTL and drop if it has reached the last hop
        packet.ttl = packet.ttl - 1
        if packet.ttl <= 0:
            self.trace("%s dropping packet due to TTL expired" % (self.hostname))
            return

        # forward the packet
        self.forward_packet(packet)


    def deliver_packet(self,packet):
        if packet.protocol not in self.protocols:
            return
        self.protocols[packet.protocol].receive_packet(packet)


    def forward_packet(self,packet):
        if packet.destination_address == 0:
            # broadcast the packet
            self.forward_broadcast_packet(packet)
        else:
            # forward the packet
            self.forward_unicast_packet(packet)

    def forward_unicast_packet(self,packet):
        if packet.destination_address not in self.forwarding_table:
            self.trace("%s no routing entry for %d" % (self.hostname,packet.destination_address))
            return
        link = self.forwarding_table[packet.destination_address]
        self.trace("%s forwarding packet to %d" % (self.hostname,packet.destination_address))
        link.send_packet(packet)

    def forward_broadcast_packet(self,packet):
        for link in self.links:
            self.trace("%s forwarding broadcast packet to %s" % (self.hostname,link.endpoint.hostname))
            packet_copy = copy.deepcopy(packet)
            link.send_packet(packet_copy)
