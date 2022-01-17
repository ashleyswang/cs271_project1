import heapq
import pickle
import socket
import sys
import threading
import time

from utilities import *

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


  '''
  Listens for incoming client connection requests.
  '''
  def listen(self):
    self.socket.listen(32)
    while True:
      sock, address = self.socket.accept()
      pid = pickle.loads(sock.recv(1024))
      self.conns[pid] = sock
      success(f"Connected to Client {pid}")
      threading.Thread(target=self.client_respond, args=(sock, pid)).start()
    self.socket.close()


  '''
  Connects to client with input PID.
  '''
  def connect(self, pid):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (socket.gethostname(), 5000+pid)
    sock.connect(address)
    self.conns[pid] = sock
    sock.sendall(pickle.dumps(self.pid))
    success(f"Connected to Client {pid}")
    threading.Thread(target=self.client_respond, args=(sock, pid)).start()

  def close(self):
    for sock in self.conns:
      if sock is not None:
        sock.close()
    self.socket.close()


  '''
  Acquires distributed mutex for client. Returns once lock is retrieved.
  '''
  def acquire(self):
    notice("Sending REQUEST to Clients...")
    self.update_llc()
    self.push_queue(self.llc, self.pid)
    llc, pid = self.llc, self.pid
    time.sleep(DELAY)

    conns_count = 0
    for sock in self.conns:
      if sock is not None: 
        sock.sendall(pickle.dumps(("REQUEST", llc, pid)))
        conns_count += 1
    
    while self.reply_count < conns_count: continue
    self.lock.acquire()
    self.reply_count = 0
    self.lock.release()
    notice(f"Received all REPLIES for {(llc, pid)}. Waiting until head of queue...")
    
    while self.queue[0] != (llc, pid): continue
    notice(f"Request {(llc, pid)} at head of queue. Ready to perform operation.")


  '''
  Releases distributed mutex to be used by next client.
  '''
  def release(self):
    notice("Sending RELEASE to Clients...")
    self.pop_queue()
    self.update_llc()
    time.sleep(DELAY)
    for sock in self.conns:
      if sock is not None:
        sock.sendall(pickle.dumps(("RELEASE", self.llc, self.pid)))


  '''
  Response thread for connected clients. Handles incoming requests for
  acquiring/releasing mutex.  
  '''
  def client_respond(self, sock, pid):
    while True:
      try:
        data = pickle.loads(sock.recv(1024))
        # log(data)

        if (data[0] == "REQUEST"):
          self.push_queue(data[1], data[2])
          info(f"Receive REQUEST {data[1:]}. Sending REPLY...")
          self.update_llc(data[1])
          time.sleep(DELAY*self.pid)
          sock.sendall(pickle.dumps(("REPLY", self.llc, self.pid)))
        elif (data[0] == "RELEASE"):
          self.pop_queue()
          info(f"Receive RELEASE {data[1:]}.")
          self.update_llc(data[1])
        elif (data[0] == "REPLY"):
          self.lock.acquire()
          self.reply_count += 1
          self.lock.release()
          info(f"Receive REPLY   {data[1:]}.")
          self.update_llc(value=data[1])
      except EOFError:
        fail(f"Disconnected from Client {pid}")
        sock.close()
        self.conns[pid] = None
        sys.exit()
    sock.close()
    self.conns[pid] = None


  '''
  Updates Lamport Logical Clock Counter
  '''
  def update_llc(self, value = None):
    self.lock.acquire()
    if (value): self.llc = max(value, self.llc) + 1
    else: self.llc += 1
    log(f"LLC: {(self.llc, self.pid)}")
    self.lock.release()


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