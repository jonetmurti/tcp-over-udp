import socket
from packet import Packet, PacketType
import os
import sys

class Receiver:

    PACKET_SIZE = 32774
    RECEIVER_TIMEOUT = 5

    def __init__(
        self, 
        address,
        filename="downloaded.txt"
    ):

        self.ip, self.port = self.init_address(address)

        if not os.path.exists('output'):
            os.makedirs('output')
        self.filepath = os.path.join("output", filename)

        self.rec_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )
        self.rec_socket.bind((self.ip, self.port))
        self.rec_socket.settimeout(self.RECEIVER_TIMEOUT)

    def __del__(self):
        try:
            self.rec_socket.close()
        except Exception as e:
            print("Error destructor :", e)
        print("closing receiver...")

    def init_address(self, address):

        temp = address.split(':')

        ip = socket.gethostbyname(socket.gethostname()) if len(temp) == 1 else temp[0] 
        port = int(temp[0]) if len(temp) == 1 else int(temp[1])

        return ip, port

    def receive(self):
        file = open(self.filepath, "w")
        seq_num = -1
        conn_phase = True

        while True:
            try:
                msg, address = self.rec_socket.recvfrom(self.PACKET_SIZE)

                rec_packet = Packet()
                rec_packet.parse(msg)

                if rec_packet.checksum_correct():
                    packet_type = PacketType.UNDEF
                    if rec_packet.packet_type == PacketType.DATA:
                        packet_type = PacketType.ACK
                    elif rec_packet.packet_type == PacketType.FIN:
                        packet_type = PacketType.FIN_ACK
                    else:
                        continue

                    expected_seq = int.from_bytes(rec_packet.sequence_number, "big")
                    if seq_num + 1 == expected_seq:
                        try:
                            file.write(rec_packet.data.decode("utf-8"))
                            seq_num += 1
                        except Exception as e:
                            print("Save error :", e)

                    sent_packet = Packet(
                        packet_type=packet_type,
                        sequence_number=seq_num
                    )
                    self.rec_socket.sendto(sent_packet.to_bin(), address)

                    if rec_packet.packet_type == PacketType.FIN:
                        conn_phase = False if conn_phase else conn_phase

            except Exception as e:
                if not conn_phase:
                    break
                print("Receive error :", e)
        
        file.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print()
        print("Error:", "Needs at least 1 argument [ip:]port [filename]")
        print()
        sys.exit(-1)

    print("starting receiver...")
    try:
        if len(sys.argv) < 2:
            receiver = Receiver(
                sys.argv[1]
            )
        else:
            receiver = Receiver(
                sys.argv[1],
                sys.argv[2]
            )

        print("receiveing file...")
        receiver.receive()
        print("file saved !")
    except Exception as e:
        print("Error :", e)