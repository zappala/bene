class Connection(object):
    ''' A transport connection between two hosts. '''
    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,app=None):
        # setup transport protocol demultiplexing
        self.transport = transport
        self.source_address = source_address
        self.source_port = source_port
        self.destination_address = destination_address
        self.destination_port = destination_port
        self.node = self.transport.node
        self.transport.bind(self,source_address,source_port,
                            destination_address,destination_port)
        # setup application delivery
        self.app = app

    def receive_packet(self, packet):
        pass

    def deliver(self, data):
        self.app.receive_packet()

    def send(self, data):
        pass
