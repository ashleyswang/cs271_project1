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
    try:
      packets = client_socket.recv(1024)
    except socket.error as e:
      fail(f'Client {address} forcibly disconnected with {e}.')
      client_socket.close()
      break
    if not packets:
      fail(f'Client {address} disconnected.')
      client_socket.close()
      break
    else:
      data = pickle.loads(packets)
      info("data received : ", data)
      sender_bal_before = blockchain.get_balance(sender_id=data[1])
      bal_receiver_before = blockchain.get_balance(sender_id=data[2])
      if (data[0]=='BALANCE'):
        return_status = blockchain.get_balance(sender_id=data[1])
      elif (data[0]=='TRANSFER'):
        status, sender_bal_after = blockchain.do_transfer(sender_id=data[1],receiver_id=data[2],amount=data[3])
        return_status = [status, sender_bal_before, sender_bal_after]
      time.sleep(2)
      client_socket.send(pickle.dumps(return_status))
      notice(f'status returned for {data[0]} operation : ', return_status)


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

