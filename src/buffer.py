class SendBuffer(object):
    ''' Send buffer for transport protocols '''
    def __init__(self):
        ''' The buffer holds a series of characters to send. The base
            is the starting sequence number of the buffer. The next
            value is the sequence number for the next data that has
            not yet been sent. The last value is the sequence number
            for the last data in the buffer.'''
        self.buffer = ''
        self.base = 0
        self.next = 0
        self.last = 0

    def available(self):
        ''' Return number of bytes available to send. This is data that
            could be sent but hasn't.'''
        return self.last - self.next

    def outstanding(self):
        ''' Return number of outstanding bytes. This is data that has
            been sent but not yet acked.'''
        return self.next - self.base

    def put(self,data):
        ''' Put some data into the buffer '''
        self.buffer += data
        self.last += len(data)

    def get(self,size):
        ''' Get the next data that has not been sent yet. Return the
            data and the starting sequence number of this data. The
            total amount of data returned is at most size bytes but may
            be less.'''
        if self.next + size > self.last:
            size = self.last - self.next
        start = self.next - self.base
        data = self.buffer[start:start+size]
        sequence = self.next
        self.next = self.next + size
        return data,sequence

    def resend(self,size,reset=True):
        ''' Get oldest data that is outstanding, so it can be
        resent. Return the data and the starting sequence number of
        this data. The total amount of data returned is at most size
        bytes but may be less. If reset is true, then all other data
        that was outstanding is now treated as if it was never sent. This
        is standard practice for TCP when retransmitting.'''
        if self.base + size > self.last:
            size = self.last - self.base
        data = self.buffer[:size]
        sequence = self.base
        if reset:
            self.next = sequence + size
        return data,sequence

    def slide(self,sequence):
        ''' Slide the receive window to the acked sequence
            number. This sequence number represents the lowest
            sequence number that is not yet acked. In other words, the
            ACK is for all data less than but not equal to this
            sequence number.'''
        acked = sequence - self.base
        self.buffer = self.buffer[acked:]
        self.base = sequence
        # adjust next in case we slide past it
        if self.next < self.base:
            self.next = self.base

class Chunk(object):
    ''' Chunk of data stored in receive buffer. '''
    def __init__(self,data,sequence):
        self.data = data
        self.length = len(data)
        self.sequence = sequence

    def trim(self,sequence,length):
        ''' Check for overlap with a previous chunk and trim this chunk
            if needed.'''
        # check for overlap
        if self.sequence < sequence + length:
            self.data = self.data[sequence+length:]
            self.length = len(self.data)
            self.sequence = sequence + length

class ReceiveBuffer(object):
    ''' Receive buffer for transport protocols '''
    def __init__(self):
        ''' The buffer holds all the data that has been received,
            indexed by starting sequence number. Data may come in out
            of order, so this buffer will order them. Data may also be
            duplicated, so this buffer will remove any duplicate
            bytes.'''
        self.buffer = {}
        # starting sequence number
        self.base = 0

    def put(self,data,sequence):
        ''' Add data to the receive buffer. Put it in order of
        sequence number and remove any duplicate data.'''
        # ignore old chunk
        if sequence < self.base:
            return
        # ignore duplicate chunk
        if sequence in self.buffer:
            if self.buffer[sequence].length >= len(data):
                return
        self.buffer[sequence] = Chunk(data,sequence)
        # remove overlapping data
        next = -1
        length = 0

        for sequence in sorted(self.buffer.keys()):
            chunk = self.buffer[sequence]
            # trim chunk if there is duplicate data from the previous chunk
            chunk.trim(next,length)
            if chunk.length == 0:
                # remove chunk
                del self.buffer[sequence]
            next = chunk.sequence
            length = len(chunk.data)
        
    def get(self):
        ''' Get and remove all data that is in order. Return the data
            and its starting sequence number. '''
        data = ''
        start = self.base
        for sequence in sorted(self.buffer.keys()):
            chunk = self.buffer[sequence]
            if chunk.sequence == self.base:
                # append the data, adjust the base, delete the chunk
                data += chunk.data
                self.base += chunk.length
                del self.buffer[chunk.sequence]
        return data,start
