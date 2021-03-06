import os
import sys
import web3 
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
# Path to Escrow.json ABI Files
PATH = "./"
# Escrow Contract Address
ESCROW_ADDRESS = "0x0bb8D9a961cF6789244130f6C4f922C414Fde651"
#########################################################
#########################################################


def main():
    try:
        # Connect to web3
        w3 = connect_to_web3(URL)       

        # Load contracts
        Escrow = load_contract(w3, os.path.join(PATH, 'Escrow.json'))   
        escrow_contract = Escrow(address=(ESCROW_ADDRESS))

        ransom_address = [] 

        # Get all ransom addresses that the escrow is in charge of
        for x in range(0, 10): 
            pos = str(9).rjust(64, '0')
            storage_key = hex(int(to_hex(w3.sha3(hexstr=pos)),16) + x)
            ransom_address.append(w3.toHex(w3.eth.getStorageAt(escrow_contract.address, storage_key)))
            #print("Ransom Address {0}".format(x), ransom_address[x])


        # format ransom addresses
        latest = w3.eth.getBlock('latest').number
        for ransom in ransom_address:
            print("0x" + ransom[26:])

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
