import os
import pickle
import socket
import sys
import threading
import time

from blockchain import Blockchain
from utilities import *

DELAY = 2

def do_exit():
  sys.stdout.flush()
  SOCKET.close()
  os._exit(0)


def handle_input():
  while True:
    try:
      inp = input()
      if inp == 'exit':
        do_exit()
      elif inp=='print':
        BLOCKCHAIN.print_blockchain()
    except EOFError:
      pass


def handle_client(socket, address):
  success(f'Server connected to {address}')
  while True:
    try:
      packets = socket.recv(1024)
    except socket.error as e:
      fail(f'Client {address} forcibly disconnected with {e}.')
      socket.close()
      break
    if not packets:
      fail(f'Client {address} disconnected.')
      socket.close()
      break
    else:
      data = pickle.loads(packets)
      info("data received : ", data)
      sender_bal_before = BLOCKCHAIN.get_balance(sender_id=data[1])
      bal_receiver_before = BLOCKCHAIN.get_balance(sender_id=data[2])
      if (data[0]=='BALANCE'):
        return_status = BLOCKCHAIN.get_balance(sender_id=data[1])
      elif (data[0]=='TRANSFER'):
        status, sender_bal_after = BLOCKCHAIN.do_transfer(sender_id=data[1],receiver_id=data[2],amount=data[3])
        return_status = [status, sender_bal_before, sender_bal_after]
      time.sleep(DELAY)
      socket.send(pickle.dumps(return_status))
      notice(f'status returned for {data[0]} operation : ', return_status)


if __name__ == "__main__":
  PORT = 8000
  SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  SOCKET.bind((socket.gethostname(), int(PORT)))
  SOCKET.listen(32)
  notice(f'Server listening on port {PORT}.')

  BLOCKCHAIN = Blockchain()

  threading.Thread(target=handle_input).start()
  
  while True:
    try:
      sock, address = SOCKET.accept()
      threading.Thread(target=handle_client, args=(sock, address)).start()
    except KeyboardInterrupt:
      do_exit()

