class Transport(Object):
    def __init__(self,node):
        self.node = node
        self.node.add_protocol(protocol="TCP",handler=self)

    def bind(self,connection,source_address,source_port,
             destination_address,destination_port):
        # setup binding so that packets we receive for this combination
        # are sent to the right socket
        tuple = (source_address,source_port,
                 destination_address,destination_port)
        self.binding[tuple] = connection

    def handle_packet(packet):
        tuple = (source_address,source_port,
                 destination_address,destination_port)
        self.binding[tuple].handle_packet(packet)
