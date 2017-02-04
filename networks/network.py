import re
import sys

sys.path.append('..')

from src.link import Link
from src.node import Node


class Network(object):
    def __init__(self, config):
        self.config = config
        self.nodes = {}
        self.address = 1
        self.build()

    def build(self):
        state = 'network'
        with open(self.config) as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                if line.strip() == "":
                    state = 'links'
                if state == 'network':
                    self.create_network(line)
                elif state == 'links':
                    self.configure_link(line)

    def create_network(self, line):
        fields = line.split()
        if len(fields) < 2:
            return
        start = self.get_node(fields[0])
        for i in range(1, len(fields)):
            end = self.get_node(fields[i])
            l = Link(self.address, start, endpoint=end)
            self.address += 1
            start.add_link(l)

    def configure_link(self, line):
        fields = line.split()
        if len(fields) < 3:
            return
        start = self.get_node(fields[0])
        l = start.get_link(fields[1])
        for i in range(2, len(fields)):
            if fields[i].endswith("bps"):
                self.set_bandwidth(l, fields[i])
            if fields[i].endswith("ms"):
                self.set_delay(l, fields[i])
            if fields[i].endswith("seconds"):
                self.set_delay(l, fields[i])
            if fields[i].endswith("pkts"):
                self.set_queue(l, fields[i])
            if fields[i].endswith("loss"):
                self.set_loss(l, fields[i])

    def get_node(self, name):
        if name not in self.nodes:
            self.nodes[name] = Node(name)
        return self.nodes[name]

    def loss(self, loss):
        for node in self.nodes.values():
            for link in node.links:
                link.loss = loss

    def set_bandwidth(self, link, rate):
        numeric_rate = self.convert(rate)
        if rate.endswith("Gbps"):
            link.bandwidth = numeric_rate * 1000000000
        elif rate.endswith("Mbps"):
            link.bandwidth = numeric_rate * 1000000
        elif rate.endswith("Kbps"):
            link.bandwidth = numeric_rate * 1000
        elif rate.endswith("bps"):
            link.bandwidth = numeric_rate

    def set_delay(self, link, delay):
        numeric_delay = self.convert(delay)
        if delay.endswith("ms"):
            link.propagation = numeric_delay / 1000.0
        if delay.endswith("seconds"):
            link.propagation = numeric_delay

    def set_queue(self, link, size):
        numeric_size = self.convert(size)
        if size.endswith("pkts"):
            link.queue_size = numeric_size

    def set_loss(self, link, loss):
        numeric_loss = self.convert(loss)
        if loss.endswith("loss"):
            link.loss = numeric_loss

    @staticmethod
    def convert(value):
        return float(re.sub("[^0-9.]", "", value))
