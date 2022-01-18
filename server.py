import socket
import threading
import time
import sys
import os


def do_exit(output_file, server_socket):
  sys.stdout.flush()
  output_file.flush()
  server_socket.close()
  os._exit(0)


def handle_input(output_file, server_socket):
  while True:
      try:
          inp = input()
          if inp == 'exit':
              do_exit(output_file, server_socket)
      except EOFError:
          pass


def handle_client(client_socket, address, output_file):
  print(f'Server connected to {address}')
  while True:
    time.sleep(2)
    client_socket.send(b'ready')
    try:
      word = client_socket.recv(1024).decode()
    except socket.error as e:
      print(f'Client {address} forcibly disconnected with {e}.')
      client_socket.close()
      break
    if not word:
      print(f'Client {address} disconnected.')
      client_socket.close()
      break
    elif word.find(' ') != -1:
      # send error and don't write if the
      # client sends more than one word
      print('Received invalid word \'{word}\' from {address}')
      client_socket.send(b'error')
    else:
      data = pickle.loads(packets)
      notice(f"Received {data[0]} from Client {data[1]}")
      s_bal_before = BLOCKCHAIN.get_balance(sender_id=data[1])
      r_bal_before = BLOCKCHAIN.get_balance(sender_id=data[2])
      if (data[0]=='BALANCE'):
        return_status = BLOCKCHAIN.get_balance(sender_id=data[1])
        info(f"Client {data[1]}: ${return_status:.2f}")
      elif (data[0]=='TRANSFER'):
        status, s_bal_after = BLOCKCHAIN.do_transfer(sender_id=data[1],receiver_id=data[2],amount=data[3])
        r_bal_after = BLOCKCHAIN.get_balance(sender_id=data[2])
        return_status = [status, s_bal_before, s_bal_after]
        info(f"Transfer: {status}\n" +
             f"{12*' '}Client {data[1]}: ${s_bal_before:.2f} --> ${s_bal_after:.2f}\n" + 
             f"{12*' '}Client {data[2]}: ${r_bal_before:.2f} --> ${r_bal_after:.2f}")
      time.sleep(DELAY)
      socket.send(pickle.dumps(return_status))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: python {sys.argv[0]} <outputFile> <serverPort>')
        sys.exit()

    PORT = sys.argv[2]
    server_socket = socket.socket()
    server_socket.bind((socket.gethostname(), int(PORT)))
    server_socket.listen(32)
    print(f'Server listening on port {PORT}.')

    output_file = open(sys.argv[1], 'w')

  threading.Thread(target=handle_input).start()
  
  while True:
    try:
      sock, address = SOCKET.accept()
      pid = pickle.loads(sock.recv(1024))
      sock.sendall(pickle.dumps(BLOCKCHAIN.get_balance(pid)))
      threading.Thread(target=handle_client, args=(sock, address)).start()
    except KeyboardInterrupt:
      do_exit()

    while True:
        try:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_client, args=(
                client_socket, address, output_file)).start()
        except KeyboardInterrupt:
            do_exit(output_file, server_socket)
