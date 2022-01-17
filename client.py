import os
import pickle
import socket
import sys
import threading
import time

from lamport import LamportMutex 
from utilities import *

DELAY = 3

def do_exit():
  MUTEX.close()
  SOCKET.close()
  os._exit(0)


def handle_input():
  while True:
    try:
      data = input().split()
    except Exception: 
      print("Invalid command. Valid inputs are 'balance', 'transfer', or 'exit/quit'.")
    
    if data[0] == "exit" or data[0] == "quit":
      do_exit()
    elif data[0] == "balance":
      get_balance()
    elif data[0] == "transfer":
      try: 
        recipient = int(data[1])
        amount = round(float(data[2].strip('$')), 2)
        if recipient not in [1, 2, 3] or recipient == PID:
          raise NameError('InvalidPID')
        make_transfer(recipient, amount)
      except ValueError:
        print("Invalid argument types. Please input a integer PID and float amount.")
      except NameError:
        print("Invalid PID recipient. Please input PID from 1-3 that is not own PID.")
    elif data[0] == "queue":
      print(MUTEX.queue)


def connect_client(): 
  info("Listening for Client Connections...")
  threading.Thread(target=MUTEX.listen).start()

  info("Requesting Connections to Clients...")
  for i in range(1, PID):
    MUTEX.connect(i)
  

def connect_server(port=8000):
  SOCKET.connect((socket.gethostname(), port))


def get_balance():
  MUTEX.acquire()

  print("Fetching Balance ...")
  MUTEX.update_llc()
  time.sleep(DELAY)
  SOCKET.sendall(pickle.dumps(("BALANCE", PID, 0, 0)))
  
  balance = pickle.loads(SOCKET.recv(1024))
  print(f"Balance: ${balance:.2f}", flush=True)

  MUTEX.release()


def make_transfer(recipient, amount):
  MUTEX.acquire()

  print("Initiating Transfer ...")
  MUTEX.update_llc()
  time.sleep(DELAY)
  SOCKET.sendall(pickle.dumps(("TRANSFER", PID, recipient, amount)))
  
  status, bal_before, bal_after = pickle.loads(SOCKET.recv(1024))
  print(f"Transfer: {status}", flush=True)
  if status=="SUCCESS":
    print(f"    Balance before: ${bal_before:.2f}", flush=True)
    print(f"    Balance after : ${bal_after:.2f}", flush=True)
  else:
    print("    You don't have enough balance to make this transaction.")
    print(f"    Current Balance: {bal_before:.2f}", flush=True)
  
  MUTEX.release()


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print(f'Usage: python {sys.argv[0]} <processId>')
    sys.exit()

  PID = int(sys.argv[1])
  MUTEX = LamportMutex(PID)
  SOCKET = socket.socket()
  
  notice(f"Client {PID}")
  notice(f'Initial Balance : $10.00')

  # Connect to Client & Server Machines
  connect_client()
  connect_server()

  # Handle User Input
  handle_input()
  do_exit()
