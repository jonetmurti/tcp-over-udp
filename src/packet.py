import struct

class PacketType():
    DATA = b'\x00'
    ACK = b'\x01'
    FIN = b'\x02'
    FIN_ACK = b'\x03'
    UNDEF = b'\x04'

class Packet():
    def __init__(self, 
                 packet_type = b'\x00',
                 length = 0, 
                 sequence_number = 0, 
                 data = "".encode("utf-8")):
        self.packet_type = struct.pack('c', packet_type)
        self.int_length = length
        self.length = struct.pack('2s', length.to_bytes(2, byteorder="big"))
        self.sequence_number = struct.pack('2s', sequence_number.to_bytes(2, byteorder="big"))
        self.data = data
        self.checksum = self.calculate_checksum()
        self.received_checksum = self.checksum
        # TODO : cek kalo length yg dimasukin == len(self.data)

    def calculate_checksum(self):
        checksum_h = self.length[0] ^ self.sequence_number[0]
        checksum_l = self.length[1] ^ self.sequence_number[1] ^ self.packet_type[0]

        data_length = int.from_bytes(self.length, "big")
        i = 0
        for i in range(0, data_length, 2):
            checksum_h ^= self.data[i]
            if i + 1 < data_length:
                checksum_l ^= self.data[i + 1]

        return struct.pack('cc', checksum_h.to_bytes(1, byteorder="big"), checksum_l.to_bytes(1, byteorder="big"))
        
    def set_packet_type(self, packet_type):
        self.packet_type = struct.pack('c', packet_type)
        self.checksum = self.calculate_checksum()

    def to_bin(self):
        return struct.pack('c2s2s2s{}s'.format(int.from_bytes(self.length, "big")), self.packet_type, self.length, self.sequence_number, self.checksum, self.data)

    def parse(self, data):
        byte_array = struct.unpack('c2s2s2s{}s'.format(len(data) - 7), data)
        
        self.packet_type = byte_array[0]
        self.length = byte_array[1]
        self.sequence_number = byte_array[2]
        self.received_checksum = byte_array[3]
        self.data = byte_array[4]
        self.checksum = self.calculate_checksum()

    def checksum_correct(self):
        return self.received_checksum == self.checksum