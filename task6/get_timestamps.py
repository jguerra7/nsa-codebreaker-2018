import os
import sys
import web3 
import datetime
from web3 import Web3
import logging
import json
import requests
from eth_utils import remove_0x_prefix, to_int, to_checksum_address, to_hex

# Setup logging
LOG = logging.getLogger("web3_demo")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

#########################################################
#### Change These Fields ###### #########################
#########################################################

### Usage: python3 victim_ids.py

# URL of Blockchain
URL = "https://codebreaker.ltsnet.net/eth/cbfc0f5b81532097/1613c2a28bbc597ad0f0361330c810986838cfbd14d450131f3d61c5fab8c65f"
# Path to Escrow.json & Ransom.json ABI Files
PATH = "./"
# Escrow Contract Address
REGISTRY_ADDRESS = "0x6b4e1e0755a93c6b60851dc72f4e32fa18ac6828"
RANSOM_ADDRESS = "0x688eEaD6Fd95c6b8041066Bed4cAC4F795d7B445"
#########################################################
#########################################################


def main():
    try:
        # Connect to web3
        w3 = connect_to_web3(URL)       

        # Load contracts
        Ransom = load_contract(w3, os.path.join(PATH, 'Ransom.json'))         
        ransom_contract = Ransom(address=(w3.toChecksumAddress(RANSOM_ADDRESS)))
 
        current = w3.eth.getBlock('latest').number
        
        for x in range(1264, 1270):
            n = w3.eth.getBlockTransactionCount(x)
            y = 0
            while (n > 0):
                t = w3.eth.getTransactionByBlock(x, y)
                print(t)
                y += 1
                n -= 1
 
    except requests.exceptions.HTTPError as http_err:
        LOG.error("web3 connection failure: {0}".format(http_err))
        return 2
    except Exception as e:
        LOG.error("Caught exception: {0}".format(e))
        return 3

    return 0

def connect_to_web3(url=None):
    if url is None: url = os.environ['URL']
    return Web3(Web3.HTTPProvider(url))

def load_contract(w3, json_path):
    with open(json_path) as fobj:
        info = json.load(fobj) 
        return w3.eth.contract(abi=info)

if __name__ == '__main__':
    sys.exit(main())
