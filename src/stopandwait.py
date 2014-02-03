from sim import Sim
from connection import Connection
from tcppacket import TCPPacket

import math

class StopAndWait(Connection):
    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,app=None):
        Connection.__init__(self,transport,source_address,source_port,
                            destination_address,destination_port,app)
        self.send_buffer = ''
        self.receive_buffer = ''
        self.packet_is_outstanding = False
        self.mss = 1000
        self.sequence = 0
        self.last_sent = 0
        self.ack = 0
        self.timer = None
        self.timeout = 1
        self.max_sequence = math.pow(2,64)

    def handle_packet(self,packet):
        # handle ACK
        if self.packet_is_outstanding and packet.ack_number == self.sequence:
            # this acks new data, so advance the send buffer, reset
            # the outstanding flag, cancel the timer, and send if possible
            Sim.trace("%d received StopAndWait ACK from %d for %d" % (packet.destination_address,packet.source_address,packet.ack_number))
            self.send_buffer = self.send_buffer[self.sequence-self.last_sent:]
            self.packet_is_outstanding = False
            self.cancel_timer()
            self.send_if_possible()
        # handle data
        if packet.length > 0:
            Sim.trace("%d received StopAndWait segment from %d for %d" % (packet.destination_address,packet.source_address,packet.sequence))
            # if the packet is the one we're expecting increment our
            # ack number and add the data to the receive buffer
            if packet.sequence == self.ack:
                self.increment_ack(packet.sequence + packet.length)
                self.receive_buffer += packet.body
                # deliver data that is in order
                self.app.handle_packet(packet)
            # always send an ACK
            self.send_ack()

    def send(self,data):
        self.send_buffer += data
        self.send_if_possible()

    def send_if_possible(self):
        if self.packet_is_outstanding:
            return
        if not self.send_buffer:
            return
        self.packet_is_outstanding = True
        packet = self.send_one_packet(self.sequence)
        self.last_sent = self.sequence
        self.increment_sequence(packet.length)

    def send_one_packet(self,sequence):
        # get one packet worth of data
        body = self.send_buffer[0:self.mss]
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           body=body,
                           sequence=sequence,ack_number=self.ack)

        # send the packet
        Sim.trace("%d sending StopAndWait segment to %d for %d" % (self.source_address,self.destination_address,packet.sequence))
        self.transport.send_packet(packet)

        # set a timer
        self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)
        return packet

    def send_ack(self):
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           sequence=self.sequence,ack_number=self.ack)
        # send the packet
        Sim.trace("%d sending StopAndWait ACK to %d for %d" % (self.source_address,self.destination_address,packet.ack_number))
        self.transport.send_packet(packet)

    def increment_sequence(self,length):
        self.sequence += length
        if self.sequence >= self.max_sequence:
            self.sequence = self.sequence - self.max_sequence

    def increment_ack(self,sequence):
        self.ack = sequence
        if self.ack >= self.max_sequence:
            self.ack = 0
        return True

    def retransmit(self,event):
        if not self.send_buffer:
            return
        if not self.packet_is_outstanding:
            return
        Sim.trace("%d retransmission timer fired" % (self.source_address))
        packet = self.send_one_packet(self.last_sent)

    def cancel_timer(self):
        if not self.timer:
            return
        Sim.scheduler.cancel(self.timer)
        self.timer = None
