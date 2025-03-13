# Reliable Data Transfer

![Static Badge](https://img.shields.io/badge/Language-Python-blue)
![GitHub repo size](https://img.shields.io/github/repo-size/christiandees/ReliableDataTransfer)
 
Reliable data transfer, or RDT, refers to the process of sending and receiving data in a way that guarantees its integrity, prevents packet loss, avoids duplication, and ensures the data is delivered in the correct order. This program is designed to handle a file upload from a client acting as the sender to a server acting as the receiver using the Stop-and-Wait protocol. This protocol ensures reliability, as mentioned above, through packet acknowledgments, sequence numbers, timeouts for retransmissions, and error detection. The client and server programs also rely on the provided helper modules, including timer.py, udt.py, and packet.py, to manage packet timers, create and send packets, and simulate packet loss. Go-Back-N will be supported in the future.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Features](#features)
3. [Libraries and Modules](#libraries-and-modules)
4. [Future Development](#future-development)


## Getting Started
To get started transferring a file, run the server. When prompted, enter port 10000 and 'snw' for the protocol. Once the server is running, there is a 5-second window before it closes the connection, so be sure to quickly run the client. The commands to run each program in the terminal are as follows:
** Ensure that the file you want to transfer is in the same directory as both the client and server
```bash
python3 server.py
python3 client.py <file_to_transfer>
```

As packets are transmitted, you may cancel the transfer at any time with **Crtl-C**

## Features
- **Stop-and-Wait Protocol**: Reliably transfer packet-by-packet.
- **Checksum Error Detection**: Detect any errors within packets via its checksum.
- **Error Management**: Gracefully handles user cancellation and any errors to occur.
- **Summary of Data**: Summary of total transmitted packets, retransmitted packets, and runtime (in seceonds).

## Libraries and Modules
Fash is built using only the following libraries:
- **packet.py**: Create and extract packets.
- **timer.py**: Timer class for each packet.
- **udt.py**: Sending and receiving of packets, simulating packet loss.
- **os**: Operating system functionality for file path.
- **sys**: System-specific parameters and functions.
- **socket**: Network communication API.
- **select**: Socket multiplexing monitoring.

## Future Development 
Implimentation of Go-Back-N protocol utilizing threading.
