class StopAndWait(Connection):
    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,app=None):
        StopAndWait.__init__(transport,source_address,source_port,
                             destination_address,destination_port,app)
        self.send_buffer = ''
        self.receive_buffer = ''
        self.packet_is_outstanding = False
        self.mss = 1500

    def handle_packet(packet):
        pass

    def send(data):
        self.send_buffer += data
        self.send_if_possible()

    def send_if_possible():
        if self.packet_is_outstanding:
            return
        # get one packet worth of data
        
