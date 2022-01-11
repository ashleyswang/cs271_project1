import socket
import threading
import time
import sys
import os
import heapq

DELAY = 3

class LamportMutex:
  def __init__(self, pid):
    self.pid = pid
    self.llc = 0
    
    self.queue = []
    self.conns = [None, None, None, None]

    self.queue_lock = threading.Lock()  # Lock for updating queue
    self.llc_lock = threading.Lock()    # Lock for updating LLC

    self.socket = socket.socket()
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind((socket.gethostname(), 5000 + self.pid))

  def listen(self):
    self.socket.listen(32)
    while True:
      sock, address = self.socket.accept()
      data = sock.recv(1024).decode("utf8")
      self.conns[int(data)] = sock
      print(f"Connected to Client {data}")
      threading.Thread(target=self.client_respond, args=(sock,)).start()
    self.socket.close()
  
  def connect(self, pid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (socket.gethostname(), 5000+pid)
    sock.connect(address)
    self.conns[pid] = sock
    sock.sendall(f"{self.pid}".encode("utf8"))
    print(f"Connected to Client {pid}")
    threading.Thread(target=self.client_respond, args=(sock,)).start()

  def close(self):
    for sock in self.conns:
      if sock is not None:
        sock.close()
    self.socket.close()

  '''
  Response thread for connected clients. Implements Lamport's Distributed
  Mutex responses to REQUEST/RELEASE flags. 
  '''
  def client_respond(self, sock):
    while True:
      data = sock.recv(1024).decode("utf8")
      print(data)

      # data = sock.recv(1024).decode("utf8").split()
      # self.update_llc()

      # # data = [ REQUEST/RELEASE, LLC, PID ]
      # if (data[0] == "REQUEST"):
      #   self.queue_lock.acquire()
      #   heapq.heappush(self.queue, (int(data[1]), int(data[2])))
      #   self.queue_lock.release()
      #   self.update_llc(value=int(data[1]))
      #   # time.sleep(DELAY)
      #   sock.sendall(f"REPLY {self.llc} {self.pid}".encode("utf8"))
      # elif (data[0] == "RELEASE"):
      #   self.queue_lock.acquire()
      #   heapq.heappop(self.queue)
      #   self.queue_lock.release()
      #   self.update_llc(value=int(data[1]))
      # else:
      #   sock.close()
      #   sys.exit()
    sock.close()

  '''
  Sends REQUEST flag to other machines to put request into queue.
  '''
  def send_request(self, sock):
    # time.sleep(DELAY)
    sock.sendall(f"REQUEST {self.llc} {self.pid}".encode("utf8"))

    while (True):
      data = sock.recv(1024).decode("utf8").split()
      if (data[0] == "REPLY"):
        self.update_llc(value=int(data[1]))
        break

  def send_release(self, sock):
    time.sleep(DELAY)
    sock.sendall(f"RELEASE {self.llc} {self.pid}".encode("utf8"))

  '''
  Updates Lamport Logical Clock
  '''
  def update_llc(self, value = None):
    self.llc_lock.acquire()
    if (value): self.llc = max(value, self.llc) + 1
    else: self.llc += 1
    self.llc_lock.release()

  '''
  Returns socket object of specified client
  '''
  def get_client(self, pid):
    return self.conns[pid]

  