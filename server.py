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
        BCHAIN.print_blockchain()
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
      op, sender, receiver, amount = pickle.loads(packets)
      notice(f"Received {op} from Client {sender}")
    
      if (op == 'BALANCE'):
        response = BCHAIN.get_balance(sender)
        info(f"Client {sender}: ${response:.2f}")
      elif (op == 'TRANSFER'):
        sender_balance = BCHAIN.get_balance(sender)
        receiver_balance = BCHAIN.get_balance(receiver)
        status = BCHAIN.make_transfer(sender, receiver, amount)
        response = [status, sender_balance, BCHAIN.get_balance(sender)]
        info(f"Transfer: {status}\n" +
             f"{12*' '}Client {sender}: ${sender_balance:.2f} --> ${BCHAIN.get_balance(sender):.2f}\n" + 
             f"{12*' '}Client {receiver}: ${receiver_balance:.2f} --> ${BCHAIN.get_balance(receiver):.2f}")
      time.sleep(DELAY)
      socket.send(pickle.dumps(response))


if __name__ == "__main__":
  PORT = 8000
  SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  SOCKET.bind((socket.gethostname(), int(PORT)))
  SOCKET.listen(32)
  notice(f'Server listening on port {PORT}.')

  BCHAIN = Blockchain()

  threading.Thread(target=handle_input).start()
  
  while True:
    try:
      sock, address = SOCKET.accept()
      pid = pickle.loads(sock.recv(1024))
      sock.sendall(pickle.dumps(BCHAIN.get_balance(pid)))
      threading.Thread(target=handle_client, args=(sock, address)).start()
    except KeyboardInterrupt:
      do_exit()

