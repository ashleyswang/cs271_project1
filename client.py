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
        amount = float(data[2].strip('$'))
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
  time.sleep(DELAY)
  SOCKET.sendall(pickle.dumps(("BALANCE", PID, 0, 0)))
  time.sleep(DELAY)
  balance = pickle.loads(SOCKET.recv(1024))
  success(f"Balance: ${balance}")
  time.sleep(1)
  MUTEX.release()


def make_transfer(recipient, amount):
  MUTEX.acquire()
  print("Initiating Transfer ...")
  time.sleep(DELAY)
  SOCKET.sendall(pickle.dumps(("TRANSFER", PID, recipient, amount)))
  time.sleep(DELAY)
  status, sender_bal_before, sender_bal_after = pickle.loads(SOCKET.recv(1024))
  info(f"Balance before transaction: {sender_bal_before}")
  if status=="SUCCESS":
    success(f"Transfer: {status}")
  else:
    fail(f"Transfer: {status}")
    fail("You don't have enough balance to make this transaction.")
  info(f"Balance after transaction: {sender_bal_after}")
  time.sleep(1)
  MUTEX.release()


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print(f'Usage: python {sys.argv[0]} <processId>')
    sys.exit()

  PID = int(sys.argv[1])
  MUTEX = LamportMutex(PID)
  SOCKET = socket.socket()
  notice(f"Client {PID}")
  notice(f'Initial Balance : $10')

  # Connect to Client & Server Machines
  connect_client()
  connect_server()

  # Handle User Input
  handle_input()
  do_exit()
