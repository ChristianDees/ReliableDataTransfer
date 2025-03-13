#!/usr/bin/env python3
# Author: Christian Dees - March 13, 2025
import socket
import sys
import udt, packet
import timer as t
import os
import time

# Create 8-bit checksum of seq_num + data
def create_checksum(seq_num, data):
    return str(sum(byte.bit_count() for byte in (data.encode() if isinstance(data, str) else data)) + seq_num).zfill(8).encode()

# Check if checksum is correct
def verify_checksum(seq_num, checksum, data):
    return checksum == create_checksum(seq_num, data)

# Handle sending the file
def send_file(file, server_address):
    fe = os.path.splitext(file)[1].encode() # File extension
    mss = 1000            # Max Seg Size
    mytimer = t.Timer(1)  # 1 second timeout
    # Pkt seq, chunk idx, tx pkts, rtx pkts
    seq_num = i = ttp = trp = 0 
    rv = (None,)*4        # Default ret val      
    # Get file data
    try:
        with open(file, 'rb') as f:
            fd = f.read()
    except FileNotFoundError:
        print(f"{file}: No such file")
        return rv
    except IOError as e:
        print(f"Error: {e}")
        return rv
    # Create a non-blocking UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    # Create chunks of size mss
    chunks = [fe] + [fd[i:i + mss] for i in range(0, len(fd), mss)]
    try:
        start_time = time.time() # Start of execution
        # Send file in MSS chunks
        while i != len(chunks):
            chunk = chunks[i]
            # Create and send chunk packet
            checksum = create_checksum(seq_num, chunk)
            pkt = packet.make(seq_num, checksum, chunk)
            udt.send(pkt, sock, server_address)
            ttp += 1
            print(f"Client: Pkt {seq_num} sent")
            # Start timer
            mytimer.start()
            ackRvd = False
            while mytimer.running() and not mytimer.timeout():
                try:
                    rcvpkt, addr = udt.recv(sock)
                    if rcvpkt:
                        ttp += 1
                        seq, checksum, dataRcvd = packet.extract(rcvpkt)
                        if verify_checksum(seq, checksum, dataRcvd):
                            ackRvd = True   # Packet has been ACK'd
                            seq_num ^= 1    # Toggle seq_num for next packet
                            print(f"Client: Ack Received {seq}")
                            mytimer.stop()
                            break
                except BlockingIOError: continue
            mytimer.stop()
            # ACK not received
            if not ackRvd:
                print("Timeout occurred, retransmitting...")
                ttp, trp = ttp + 1, trp + 1
                continue
            else: i += 1  # Move onto next chunk  
    except KeyboardInterrupt: print('Client: File transfer stopped. Exiting...')
    # After all chunks are sent, send the EOF packet
    udt.send(packet.make(seq_num, create_checksum(seq_num, '\\EOF'.encode()), '\\EOF'.encode()), sock, server_address)
    print("Client: EOF sent")
    sock.close()
    return ttp + 1, trp, start_time, time.time()

# Summary of transfer
def print_results(ttp, trp, start_time, end_time):
    duration = end_time - start_time
    print(f"{'-' * 50}\n{'RESULTS SUMMARY'.center(50, '-')}\n{'-' * 50}")
    print(f"Total Transmitted Packets: {ttp or 0}")
    print(f"Total Retransmitted Packets: {trp}")
    print(f"Total Time Taken: {duration:.3f} {'second' if duration == 1 else 'seconds'}")

def main():
    # Check args
    if len(sys.argv) != 2: sys.exit("Usage: python3 client.py <file_to_transfer>")
    # Get file to transfer
    file = sys.argv[1]
    server_address = ('localhost', 10000)
    ttp, trp, start_time, end_time = send_file(file, server_address)
    print(f"Client: File Transfer {'Complete' if ttp else 'Failed'}")
    if ttp: print_results(ttp, trp, start_time, end_time)

if __name__ == "__main__":
    main()