import json
from hashlib import sha256
from utilities import *


class Blockchain:
  def __init__(self):
    self.chain = [0]
    self.balances = {1: 10.0, 2: 10.0, 3: 10.0}


  ''' Get balance of client with given PID'''
  def get_balance(self, pid):
    return self.balances[pid]
  

  ''' Add amount to balance of client with given PID'''
  def update_balance(self, pid, amount):
    self.balances[pid] = round(self.balances[pid] + amount, 2)


  ''' Makes transfer if sender has sufficient funds'''
  def make_transfer(self, sender, receiver, amount):
    # check balance 
    if self.balances[sender] < amount:
      return "INCORRECT"
    
    # if valid, create a new block and update balances
    self.create_block(sender, receiver, amount)
    self.update_balance(sender, -amount)
    self.update_balance(receiver, amount)
    return "SUCCESS"


  ''' Creates new block on the blockchain '''
  def create_block(self, sender, receiver, amount):
    block= {'index': len(self.chain)-1,
            'previous_hash': self.hashify(self.chain[-1]),
            'sender': sender,
            'receiver': receiver,
            'amount': amount
          }  
    self.chain.append(block)


  ''' Hashes input block using SHA256'''
  def hashify(self, block):
    json_string = json.dumps(block, sort_keys=True).encode()
    hash = sha256(json_string).hexdigest()
    return hash

  
  ''' Prints blockchain '''
  def print_blockchain(self):
    if len(self.chain)==1:
      print("Blockchain is empty")
    else:
      log("START")
      for block in self.chain[1:]:
        print(f"Previous Hash: {block['previous_hash']}")
        success(f"Client {block['sender']} pays Client {block['receiver']} ${block['amount']}")
        print("----->")
      log("END")