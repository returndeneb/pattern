# app.py (Blockchain 기반 리팩토링)
from flask import Flask, request, jsonify, render_template
import hashlib
import json
import os
import time

app = Flask(__name__)
CHAIN_FILE = 'blockchain.json'

def create_genesis_block():
    return {
        'index': 0,
        'timestamp': time.time(),
        'commitment': 'Genesis Block',
        'previous_hash': '0',
        'hash': hashlib.sha256('Genesis Block'.encode()).hexdigest()
    }

def load_blockchain():
    if not os.path.exists(CHAIN_FILE):
        with open(CHAIN_FILE, 'w') as f:
            json.dump([create_genesis_block()], f, indent=2)
    with open(CHAIN_FILE, 'r') as f:
        return json.load(f)

def save_blockchain(chain):
    with open(CHAIN_FILE, 'w') as f:
        json.dump(chain, f, indent=2)

def get_last_block():
    chain = load_blockchain()
    return chain[-1]

def add_vote_block(commitment):
    chain = load_blockchain()
    last_block = chain[-1]
    block = {
        'index': last_block['index'] + 1,
        'timestamp': time.time(),
        'commitment': commitment,
        'previous_hash': last_block['hash']
    }
    block['hash'] = hashlib.sha256((str(block['index']) + str(block['timestamp']) + commitment + block['previous_hash']).encode()).hexdigest()
    chain.append(block)
    save_blockchain(chain)
    return block['hash']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    vote = data.get("vote")
    salt = data.get("salt")
    if not vote or not salt:
        return jsonify({"error": "Missing vote or salt"}), 400
    commitment = hashlib.sha256((vote + salt).encode()).hexdigest()
    block_hash = add_vote_block(commitment)
    return jsonify({"message": "Vote recorded on blockchain", "receipt": commitment, "block_hash": block_hash})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    salt = data.get("salt")
    if not salt:
        return jsonify({"error": "Missing salt"}), 400
    chain = load_blockchain()
    for block in chain[1:]:  # skip genesis block
        if block['commitment'].endswith(salt):
            return jsonify({"valid": True})
    return jsonify({"valid": False})

if __name__ == '__main__':
    app.run(debug=True)
