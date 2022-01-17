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
      notice(f"Received {data[0]} from Client {data[1]}")
      sender_bal_before = BLOCKCHAIN.get_balance(sender_id=data[1])
      receiver_bal_before = BLOCKCHAIN.get_balance(sender_id=data[2])
      if (data[0]=='BALANCE'):
        return_status = BLOCKCHAIN.get_balance(sender_id=data[1])
        info(f"Client {data[1]}: ${return_status:.2f}")
      elif (data[0]=='TRANSFER'):
        status, sender_bal_after = BLOCKCHAIN.do_transfer(sender_id=data[1],receiver_id=data[2],amount=data[3])
        receiver_bal_after = BLOCKCHAIN.get_balance(sender_id=data[2])
        return_status = [status, sender_bal_before, sender_bal_after]
        info(f"Transfer: {status}\n{12*' '}Client {data[1]}: {sender_bal_before:.2f} --> {sender_bal_after:.2f}\n{12*' '}Client {data[2]}: {receiver_bal_before:.2f} --> {receiver_bal_after:.2f}")
      time.sleep(DELAY)
      socket.send(pickle.dumps(return_status))


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

