import heapq
import os
import pickle
import socket
import sys
import threading
import time

DELAY = 1

class LamportMutex:
  def __init__(self, pid):
    self.pid = pid
    self.llc = 0

    self.queue = []
    self.conns = [None, None, None, None]
    self.reply_count = 0
    
    self.lock = threading.Lock()

    self.socket = socket.socket()
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind((socket.gethostname(), 5000 + self.pid))

  def listen(self):
    self.socket.listen(32)
    while True:
      sock, address = self.socket.accept()
      pid = pickle.loads(sock.recv(1024))
      self.conns[pid] = sock
      print(f"Connected to Client {pid}")
      threading.Thread(target=self.client_respond, args=(sock, pid)).start()
    self.socket.close()
  
  def connect(self, pid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (socket.gethostname(), 5000+pid)
    sock.connect(address)
    self.conns[pid] = sock
    sock.sendall(pickle.dumps(self.pid))
    print(f"Connected to Client {pid}")
    threading.Thread(target=self.client_respond, args=(sock, pid)).start()

  def close(self):
    for sock in self.conns:
      if sock is not None:
        sock.close()
    self.socket.close()

  '''
  Response thread for connected clients. Implements Lamport's Distributed
  Mutex responses to REQUEST/RELEASE flags. 
  '''
  def client_respond(self, sock, pid):
    while True:
      try:
        data = pickle.loads(sock.recv(1024))
        print(data)

        if (data[0] == "REQUEST"):
          self.push_queue(data[1], data[2])
          self.update_llc(data[1])
          print(f"Received REQUEST from {data[2]}. Send REPLY.")
          time.sleep(DELAY*self.pid)
          sock.sendall(pickle.dumps(("REPLY", self.llc, self.pid)))
        elif (data[0] == "RELEASE"):
          self.pop_queue()
          self.update_llc(data[1])
          print(f"Received RELEASE from {data[2]}.")
        elif (data[0] == "REPLY"):
          self.lock.acquire()
          self.reply_count += 1
          self.lock.release()
          self.update_llc(value=data[1])
          print(f"Received REPLY from {data[2]}.")
      except EOFError:
        sock.close()
        self.conns[pid] = None
        sys.exit()
    sock.close()
    self.conns[pid] = None

  '''
  Send a REQUEST to each client. Returns once all REPLIES are 
  received and request is at head of queue.
  '''
  def client_request(self):
    self.update_llc()
    self.push_queue(self.llc, self.pid)
    request = (self.llc, self.pid)
    time.sleep(DELAY)

    conns_count = 0
    for sock in self.conns:
      if sock is not None: 
        sock.sendall(pickle.dumps(("REQUEST", self.llc, self.pid)))
        conns_count += 1
    
    while self.reply_count < conns_count: continue
    self.lock.acquire()
    self.reply_count = 0
    self.lock.release()
    print(f"Received all REPLIES for {request}. Waiting until head of queue...")
    
    while self.queue[0] != request: continue
    print(f"Request {request} at head of queue. Ready to perform operation.")

  '''
  Sends RELEASE flag to all clients. 
  '''
  def client_release(self):
    self.pop_queue()
    self.update_llc()
    time.sleep(DELAY)
    for sock in self.conns:
      if sock is not None:
        sock.sendall(pickle.dumps(("RELEASE", self.llc, self.pid)))

  '''
  Updates Lamport Logical Clock
  '''
  def update_llc(self, value = None):
    self.lock.acquire()
    if (value): self.llc = max(value, self.llc) + 1
    else: self.llc += 1
    self.lock.release()

  '''
  Returns socket object of specified client
  '''
  def get_client(self, pid):
    return self.conns[pid]
  
  '''
  Adds request to queue
  '''
  def push_queue(self, llc, pid):
    self.lock.acquire()
    heapq.heappush(self.queue, (llc, pid))
    self.lock.release()

  '''
  Removes request from queue
  '''
  def pop_queue(self):
    self.lock.acquire()
    heapq.heappop(self.queue)
    self.lock.release()