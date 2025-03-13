# Author: Christian Dees - March 13, 2025
import socket
import udt, packet
import select  

# Create 8-bit checksum of sum
def create_checksum(seq_num, data):
    return str(sum(byte.bit_count() for byte in (data.encode() if isinstance(data, str) else data)) + seq_num).zfill(8).encode()

# Check if checksum is correct
def verify_checksum(seq_num, checksum, data):
    return checksum == create_checksum(seq_num, data)

# Handle recieving a file
def recv_file(sock, protocol):
    # expected, seq, file ext recv, file ext, name
    exp_seq, feRecvd, fe, filename = 0, False, b'', None
    eof = b'\\EOF' # EOF indicator
    try:
        while True:
            # Timeout socket for 5 seconds
            ready = select.select([sock], [], [], 5)  
            if ready[0]:
                pkt, addr = udt.recv(sock) # Get da packet
                # Create filename with client's IP and port
                if not filename and fe: filename = f"received_{addr[0]}_{addr[1]}{fe.decode()}"
                if pkt:
                    seq, checksum, data = packet.extract(pkt)
                    # Ignore packet if needed
                    if not verify_checksum(seq, checksum, data):
                        print("Server: Checksum incorrect, ignoring packet")
                        continue
                    # Write data
                    if seq == exp_seq and data != eof:
                        if feRecvd and filename: 
                            # Append chunk to file 
                            with open(filename, 'ab') as f: f.write(data)
                        else: feRecvd, fe = True, data # Get file extension
                        if protocol == 'snw': exp_seq ^= 1 # Toggle seq num
                    else: print(f'Server: Expected {exp_seq}, received {seq}')
                    # Send ACK
                    ackpkt = packet.make(seq, create_checksum(seq, f'ACK - {seq}'), bytes(f'ACK - {seq}', 'utf-8'))
                    udt.send(ackpkt, sock, addr)
                    print(f'Server: ACK sent - {seq}')
                    # Check EOF
                    if data == eof:
                        print('Server: File transfer complete')
                        break
            else:
                print("Server: No packet received in 5 seconds, closing socket.")
                break
    except KeyboardInterrupt: print('Server: File transfer stopped. Exiting...')
    # Display completion
    sock.close()
    print("Server: Socket closed.")
    return filename

def main():
    # Get port and protocol
    port = int(input('Enter port: '))
    while ((protocol := input('Enter protocol (SnW/GBN): ').strip().lower()) != 'snw'): print('Invalid protocol, please try again.')
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', port)
    sock.bind(server_address)
    # Hardcode snw cuz gbn not implimented yet
    print(f'Server listening on port {port} using snw protocol...')
    # Begin file transfer
    filename = recv_file(sock, protocol)
    print("-" * 75)
    print(f"File saved as '{filename}'".center(75, "-") if filename else "No file created".center(75, "-"))
    print("-" * 75)

if __name__ == '__main__':
    main()