import socket
import sys
from packet import Packet, PacketType
import threading
import os

class Sender:

    SEND_TIMEOUT = 0.1
    PACKET_SIZE = 32774
    DATA_SIZE = 32767

    def __init__(self, filepath, addresses):
        self.receiver_list = self.init_receiver(addresses)
        self.filepath = filepath

    def init_receiver(self, addresses):
        receiver_list = []

        ip_port_list = addresses.split(',')

        for ip_port in ip_port_list:
            temp = ip_port.split(':')

            ip = socket.gethostbyname(socket.gethostname()) if len(temp) == 1 else temp[0] 
            port = int(temp[0]) if len(temp) == 1 else int(temp[1])


            receiver_list.append((ip, port))

        return receiver_list

    def main(self):
        thread_list = []
        thread_id = 0

        for receiver in self.receiver_list:
            client_thread = threading.Thread(
                target=self.handle_receiver,
                args=(receiver, thread_id,)
            )
            client_thread.start()
            thread_list.append(client_thread)
            thread_id += 1

        for t in thread_list:
            t.join()

    def handle_receiver(self, address, thread_id):
        succ = True

        try:
            handler_sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
            handler_sock.settimeout(self.SEND_TIMEOUT)
        except:
            succ = False

        seq_num = 0
        retry = 0
        create_packet = True

        try:
            file = open(self.filepath, "r")
            num_of_packet = int(os.stat(self.filepath).st_size/self.DATA_SIZE) + 1
            data = file.read(self.DATA_SIZE)
            next_data = file.read(self.DATA_SIZE)
        except:
            succ = False

        while succ and retry < 100:
            if create_packet:
                packet_type = PacketType.DATA if next_data else PacketType.FIN
                sent_packet = Packet(
                    packet_type,
                    len(data),
                    seq_num,
                    data.encode("utf-8")
                )
                data = next_data
                next_data = file.read(self.DATA_SIZE)

            ret = self.send(handler_sock, address, sent_packet)

            if ret == seq_num:
                retry += 1
                create_packet = False
            else:
                retry = 0
                seq_num = ret
                create_packet = True
                print("packet sent for receiver {rec_id} : {seq_num}/{total_packet}".format(
                        rec_id = thread_id,
                        seq_num = seq_num,
                        total_packet = num_of_packet
                    ))

            if seq_num == num_of_packet:
                break

        try:
            file.close()
        except Exception as e:
            print("Error closing file :", e)
    
        try:
            handler_sock.close()
        except Exception as e:
            print("Error closing socket :", e)

        if retry == 100:
            print("Unable to connect to receiver :", thread_id)
        print("closing thread :", thread_id)

    def send(self, sock, address, packet):
        next_seq_num = int.from_bytes(packet.sequence_number, "big")
        try:
            sock.sendto(packet.to_bin(), address)

            msg = sock.recv(self.PACKET_SIZE)
            rec_packet = Packet()
            rec_packet.parse(msg)

            if rec_packet.checksum_correct():
                if (rec_packet.sequence_number == packet.sequence_number and 
                    (rec_packet.packet_type == PacketType.ACK or rec_packet.packet_type == PacketType.FIN_ACK)):

                    next_seq_num += 1

        except Exception as e:
            print("Error thread {} :".format(thread_id), e)

        finally:
            return next_seq_num


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print()
        print("Error:", "Needs 2 arguments (filepath, address_list)")
        print("address_list format :", "[ip:]port[,[ip:]port]")
        print()
        sys.exit(-1)

    try:
        sender = Sender(sys.argv[1], sys.argv[2])
    except Exception as e:
        print("main thread error :", e)
        sys.exit(-1)
    
    print("starting sender...")

    sender.main()

    print("closing sender...")