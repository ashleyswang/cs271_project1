from hashlib import sha256
import json
from utilities import *



class Blockchain:
  def __init__(self):
    self.chain = []
    self.state = {}
    self.new_block(previous_hash = 0)

  def new_block(self, sender_id = '', receiver_id = '', previous_hash=0, amount=0):
    block= {'index': len(self.chain),
            'previous_hash': previous_hash,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'amount': amount
          }  
    self.chain.append(block)
    return block

  def last_block(self):
    return self.chain[-1]

  def hashify(self,block):
    json_string = json.dumps(block, sort_keys=True).encode()
    hash = sha256(json_string).hexdigest()
    return hash

  def set_state(self, sender_id, receiver_id,amount):
    if sender_id in self.state and self.state[sender_id]>amount:
      self.state[sender_id] = round(self.state[sender_id]-amount, 2)
    if receiver_id in self.state:
      self.state[receiver_id] = round(self.state[receiver_id]+amount, 2)

  def get_balance(self, sender_id):
    if sender_id not in self.state:
      self.state[sender_id]= 10
    return self.state[sender_id]
  
  def do_transfer(self, sender_id, receiver_id, amount):
    # check balance 
    if self.get_balance(sender_id)<amount:
      return ["INCORRECT",self.state[sender_id]]
    
    # if valid, create a new block and add it to the blockchain
    last_block = self.last_block()
    previous_hash = self.hashify(last_block)
    block = self.new_block(sender_id=sender_id, receiver_id=receiver_id, previous_hash=previous_hash, amount=amount)
    
    # update the balance state dict for sender and receiver 
    self.set_state(sender_id=sender_id, receiver_id=receiver_id, amount=amount)
    return ["SUCCESS",self.state[sender_id]]


  def print_blockchain(self):
    if len(self.chain)==1:
      print("Blockchain is empty")
    else:
      log("START")
      for block in self.chain[1:]:
        print(f"Previous Hash: {block['previous_hash']}")
        success(f"Client {block['sender_id']} pays Client {block['receiver_id']} ${block['amount']}")
        print("----->")
      log("END")
  