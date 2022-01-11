## Connecting Clients To Each Other

We want to open a two-way socket between each pair of clients. To do so, each client has two threads: listen and connect. Depending on the PID of the client, they may run either or both of the threads.

Client behavior based on PID:
- Client 1: listens for Client 2 & 3
- Client 2: connects to Client 1, listens for Client 3
- Client 3: connects to Client 1 & 2

This behavior is automatically executed once the client is started. No additional steps to connect to clients are needed. 
> Please note only valid PIDs are 1, 2, and 3.   

Questions for TA:
- blockchain is only stored on server? is there also a local copy of it for each client? or is it stored distributed-ly?
- when I do an operation how do the other machines know about it?
- prof mentioned he wanted to do it on separate hosts, does this mean we need 3 computers? (I was thinking originally he just wanted like 3 runs of the client code we had but they could be on the same computer. Just want to check that I'm not understanding this incorrectly.)