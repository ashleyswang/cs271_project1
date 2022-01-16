import socket
import threading
import time
import sys
import os
import pickle
from utilities import *
from blockchain import Blockchain


def do_exit(server_socket):
  sys.stdout.flush()
  server_socket.close()
  os._exit(0)


def handle_input(server_socket):
  while True:
      try:
          inp = input()
          if inp == 'exit':
            do_exit(server_socket)
          elif inp=='print blockchain':
            blockchain.print_blockchain()
      except EOFError:
          pass


def handle_client(client_socket, address):
  success(f'Server connected to {address}')
  while True:
    time.sleep(2)
    client_socket.send(b'ready')
    try:
      data = pickle.loads(client_socket.recv(1024))
    except socket.error as e:
      fail(f'Client {address} forcibly disconnected with {e}.')
      client_socket.close()
      break
    if not data:
      fail(f'Client {address} disconnected.')
      client_socket.close()
      break
    else:
      print("data === ", data)
      bal_sender = blockchain.get_balance(sender_id=data[1])
      bal_receiver = blockchain.get_balance(sender_id=data[2])
      if (data[0]=='BALANCE'):
        return_status = blockchain.get_balance(sender_id=data[1])
      elif (data[0]=='TRANSFER'):
        return_status = blockchain.do_transfer(sender_id=data[1],receiver_id=data[2],amount=data[3])
      time.sleep(2)
      print('balance : ', return_status)
      client_socket.sendall(pickle.dumps(return_status))
      print("sent")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: python {sys.argv[0]} <outputFile> <serverPort>')
        sys.exit()

    PORT = sys.argv[2]
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((socket.gethostname(), int(PORT)))
    server_socket.listen(32)
    notice(f'Server listening on port {PORT}.')

    threading.Thread(target=handle_input, args=((server_socket,))).start()
    blockchain= Blockchain()

    while True:
        try:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_client, args=(
                client_socket, address)).start()
        except KeyboardInterrupt:
            do_exit(server_socket)

