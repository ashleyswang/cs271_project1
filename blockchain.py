from hashlib import sha256
import os
import sys
import numpy as np
import pandas as pd
import time
import random
import json
import pickle
import math

"""
block format:
id
operation (string representation)
nonce
hash
pointer (id of previous block)
hash_pointer (hash of previous block)
"""

class Blockchain:
    def __init__(self, file="", pid=-1, csv_bytes=""):
        self._columns = ['id', 'operation', 'nonce', 'hash', 'pointer', 'hash_pointer']
        self._currhashpointer = ""
        self._pid = pid
        self._filename = file
        self._filepath = ""
        self._blockchain = ""
        self._keystore = {}
        self._csv_bytes = csv_bytes
        self._initialize()

    def _initialize(self):
        self.load_filepath(self._filename)
        self.load_blockchain()
        self.load_keystore()

    def load_filepath(self, file):
        datafile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/')
        if os.path.exists(datafile) == False:
            os.mkdir(datafile)
        if self._pid != -1:
            _tempname = 'blockchain' if self._filename == "" else self._filename
            _filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/{0}/{1}.csv'.format(self._pid, _tempname))
            os.makedirs(os.path.dirname(_filepath), exist_ok=True)
            if os.path.exists(_filepath):
                self._filepath = _filepath
                self._filename = _tempname + '.csv'
            else:
                open(_filepath, 'w')
                self._filepath = _filepath
                self._filename = _tempname + '.csv'
        elif file == "":
            _filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/blockchain.csv')
            if os.path.exists(_filepath):
                self._filepath = _filepath
                self._filename = 'blockchain.csv'
            else:
                open(_filepath, 'w')
                self._filepath = _filepath
                self._filename = 'blockchain.csv'
        else:
            _filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/{filename}'.format(filename=file))
            if os.path.exists(_filepath):
                self._filepath = _filepath
            else:
                open(_filepath, 'w')
                self._filepath = _filepath

    def load_keystore(self):
        for index, row in self._blockchain.iterrows():
            _data = row['operation'].split('[')
            if _data[0] == 'put':
                _value = _data[1].split(':')
                self._keystore[_value[0]] = _value[1][:-1]

    def load_blockchain(self):
        if self._csv_bytes != "":
            self._blockchain = pickle.loads(self._csv_bytes)
        elif os.path.exists(self._filepath):
            try:
                _blockchain = pd.read_csv(self._filepath)
                self._blockchain = _blockchain
                id, block = self.load_block()
                if block is not None:
                    self.set_hashpointer(block.at[id, 'operation'], block.at[id, 'nonce'], block.at[id, 'hash'], True)
            except Exception as e:
                self._blockchain = pd.DataFrame(columns=self._columns)
        else:
            raise Exception("file doesn't exist in /data folder")

    def calculate_nonce(self, data):
        if data[0].lower() == "get":
            operation = "{0}[{1}]".format(data[0], data[1])
        else:
            operation = "{0}[{1}:{2}]".format(data[0], data[1], data[2])
        nonce = str(random.randint(1, sys.maxsize))
        bhash = sha256("{0}{1}".format(operation, nonce).encode()).hexdigest()
        start = time.time()
        while True:
            if bhash[-1].isdigit() and int(bhash[-1]) < 3:
                end = time.time()
                return nonce, bhash, self._currhashpointer
            else:
                nonce = str(random.randint(1, sys.maxsize))
                bhash = sha256("{0}{1}".format(operation, nonce).encode()).hexdigest()

    def load_block(self): #read the latest 'head' block
        if self._blockchain.empty:
            return None
        column = self._blockchain['id']
        curr_id = column.max()
        block = self._blockchain.loc[self._blockchain['id'] == curr_id]
        return curr_id, block

    def write_to_blockchain(self, data, nonce):
        if data[0].lower() == "get":
            operation = "{0}[{1}]".format(data[0], data[1])
        else:
            operation = "{0}[{1}:{2}]".format(data[0], data[1], data[2])
        bhash = sha256("{0}{1}".format(operation, nonce).encode()).hexdigest()
        if self._blockchain.empty:
            curr_id = -1
            id = 0
        else:
            column = self._blockchain['id']
            curr_id = column.max()
            id = curr_id + 1
        _data = [[id, operation, nonce, str(bhash), curr_id, self._currhashpointer]]
        df = pd.DataFrame(_data, columns=self._columns)
        self._blockchain = self._blockchain.append(df, ignore_index=True)
        if data[0] == 'put':
            self._keystore[data[1]] = data[2]
        hptr = self._currhashpointer
        self.set_hashpointer(data, nonce, bhash)
        return self._keystore.get(data[1]), bhash, hptr
    
    def write_to_blockchain_file(self):
        self._blockchain.to_csv(path_or_buf=self._filepath, index=False)

    def set_hashpointer(self, data, nonce, hash, data_string=False):
        if data_string:
            operation = data
        else:
            if data[0].lower() == "get":
                operation = "{0}[{1}]".format(data[0], data[1])
            else:
                operation = "{0}[{1}:{2}]".format(data[0], data[1], data[2])
        self._currhashpointer = str(sha256("{0}{1}{2}".format(operation, nonce, hash).encode()).hexdigest())

    def write(self, data):
        nonce = self.calculate_nonce(data)
        self.write_to_blockchain(data, nonce)

    def save(self):
        self.write_to_blockchain_file()

    def print(self):
        print(self._blockchain)

    def print_kv(self):
        for key in self._keystore:
            print(f"\t{key}\t{self._keystore[key]}")
        print("> ", end="")

    def print_blockchain(self):
        if self.depth() == 0:
            print("empty blockchain")
            return
        #print('{:<16} {:<16} {:<16} {:<16}'.format('operation', 'hash(last 5)', 'hash_ptr(last 5)', 'nonce'))
        for index, row in self._blockchain.iterrows():
            #print('hash pointer: ', row['hash_pointer'])
            #if (type(row['hash_pointer']) == str and len(row['hash_pointer']) == 0):
            #    _hsh = "None"
            #elif type(row['hash_pointer']) == float and math.isnan(row['hash_pointer']) or row['hash_pointer'] is None:
            #    _hsh = "None"
            #else:
            #    _hsh = row['hash_pointer'][-5:]
            _str = "{:<16} {:<16} {:<16}".format(row['hash'][-5:], row['nonce'][-5:], row['operation'])
            print(_str)

    def keystore_get(self, key):
        return self._keystore.get(key)

    def depth(self):
        return len(self._blockchain)