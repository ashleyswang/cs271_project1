import socket
import threading
import time
import sys
import os
import heapq

from lamport import LamportMutex 

queue = []                  # Queue of requests
clients = []                # Sockets for connected clients

LOCK = threading.Lock()     # Lock for Priority Queue Requests
LLC_LOCK = threading.Lock() # Lock for updating

def do_exit():
  mutex.close()
  os._exit(0)

def handle_input():
  while True:
    user_input = input()
    if user_input == "exit" or user_input == "quit":
      do_exit()
    elif user_input == "request":
      request()
    elif user_input == "release":
      release()
    elif user_input == "queue":
      print(mutex.queue)
    # elif user_input == "balance":
    #   pass
      # start new thread that gets the balance
    else:
      # pid, data = user_input.split(maxsplit=1)
      # sock = mutex.get_client(int(pid))
      # sock.sendall(data.encode("utf8")) 
      pass

def listen(): 
  print("Listening for Client Connections...")
  threading.Thread(target=mutex.listen).start()
  
def connect():
  print("Requesting Connections to Clients...")
  for i in range(1, PID):
    mutex.connect(i)

def request():
  print("Sending REQUEST to Clients...")
  threading.Thread(target=mutex.client_request).start()

def release():
  print("Sending RELEASE to Clients...")
  threading.Thread(target=mutex.client_release).start()

def balance():
  threading.Thread(target=bc.get_balance).start()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print(f'Usage: python {sys.argv[0]} <processId>')
    sys.exit()

  PID = int(sys.argv[1])
  mutex = LamportMutex(PID)

  # Connect to Client Machines
  listen()
  connect()

  # TODO: Connects to Server Machine
  handle_input()
  do_exit()
