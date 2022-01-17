## Connecting Clients To Each Other

We want to open a two-way socket between each pair of clients. To do so, each client has two threads: listen and connect. Depending on the PID of the client, they may run either or both of the threads.

Client behavior based on PID:
- Client 1: listens for Client 2 & 3
- Client 2: connects to Client 1, listens for Client 3
- Client 3: connects to Client 1 & 2

This behavior is automatically executed once the client is started. No additional steps to connect to clients are needed if running Client 1, 2, and 3 in that order.
> Please note only valid PIDs are 1, 2, and 3.   

## Connecting Clients to Blockchain Server

Each client will try to connect to the blockchain server upon booting. Since we have no mechnism to manually connect to the server, the server should be ran on PORT 8000 before the clients are started. 