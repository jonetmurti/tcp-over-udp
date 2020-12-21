# ... File Sender/Receiver

## Description

The aim of this project is to implement a protocol similar to TCP over a UDP based socket

## How to run

To run sender :

1. open src folder in a terminal
2. run :

   ```python
   python sender.py <filepath> <receiver addresses>
   ```

3. receiver addresses format : 'ip1:port1,ip2:port2,...'

To run receiver :

1. open src folder in a terminal
2. run :

   ```python
   python receiver.py <address> <filename to be saved>
   ```

3. address format : 'ip:port'
