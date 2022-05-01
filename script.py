import json
import re
from operator import itemgetter
from os import path
from time import sleep

from requests_html import HTMLSession
# from web3 import Web3

# https://web3py.readthedocs.io/en/stable/web3.main.html

# web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/6995c66122144513a1bc87c8074638c5'))


s = HTMLSession()

def tvl_gainer():
    """Fetching TVL evolution of chains"""
    # Compute % change of the chain's TVL
    variation = lambda x, y: round((x - y) / y * 100, 2)
   
    if path.exists("files/TVLS.json"):
    
        # Getting old TVL data
        with open("files/TVLS.json") as file:
            old_data = json.load(file)
    
        # Fetching fresh data (chain, TVL)
        res = s.get("https://api.llama.fi/chains").json()
        new_data = dict([(c["name"], round(c["tvl"], 2)) for c in res if c["name"] in old_data])
        
        # Comparing (applying variation func to each chain then sorting result)
        changes = dict([(chain, variation(old_data[chain], new_data[chain])) for chain in new_data])
        
        sorted_changes = sorted(changes.items(), key=itemgetter(1), reverse=True)
        
        with open("tvls_evolution.json", "w") as file:
            json.dump(dict(sorted_changes), file)
            
        print("tvls_evolution.json created.")
    
    # Update the file
    with open("files/TVLS.json", "w") as file:
        res = s.get("https://api.llama.fi/chains").json()
        json.dump(dict([(c["name"], round(c["tvl"], 2)) for c in res if c["tvl"] > 0]), file)
    print("File updated.")
    
        

def fetch_tx_number():
    """Function to get the Tx number of a chain
    using scraping / api"""
    
    explorers = {
    "ethereum": "https://etherscan.io/",
    "avalanche": "https://snowtrace.io/",
    "fantom": "https://ftmscan.com/",
    "polygon": "https://polygonscan.com/",
    "arbitrum": "https://arbiscan.io/",
    "optimism": "https://optimistic.etherscan.io/",
    "bsc": "https://bscscan.com/",
    "metis": "https://andromeda-explorer.metis.io/",
    "solana": ""
}
    
    tx_number = dict()
    for chain in explorers:
        if chain == "metis":
            r = s.get(f"{explorers[chain]}")
            number = r.html.xpath('/html/body/div[1]/main/div/div/div/div[3]/div/div[2]/div/span')[0].text
            tx_number[chain] = int(number.replace(",", "").replace(",", ""))
            continue
        
        if chain == "solana":
            json_data = {
                    'method': 'getEpochInfo',
                    'jsonrpc': '2.0',
                    'params': [],
                    'id': 'e013e367-b20a-40f7-b742-6f7636f28029',
                }

            r = s.post('https://explorer-api.mainnet-beta.solana.com/', json=json_data).json()
            number = r['result']['transactionCount']
            tx_number[chain] = number
            continue
        
        
        r = s.get(f"{explorers[chain]}txs")
        element = r.html.xpath('//*[@id="ContentPlaceHolder1_topPageDiv"]/p/span[1]/text()')
        number = re.findall(r'[\d]+[.,\d]+', " ".join(element))[0]
        
        tx_number[chain] = int(number.replace(",", "").replace(" ", ""))
    
    return tx_number


def compare_tx_number():
    retry_count = 0
    with open("files/chains_tx.json") as file:
        old_data = json.load(file)
    
    new_data = fetch_tx_number()
    # Compute % change of the tx number
    variation = lambda x, y: round((x - y) / y * 100, 6)
    
    # Comparing (applying variation func to each chain then sorting result)
    try:
        changes = dict([(chain, variation(new_data[chain], old_data[chain])) for chain in new_data])
    except Exception:
        if retry_count < 4:
            print("Error, next try in 10 seconds.")
            sleep(10)
            compare_tx_number()
            retry_count += 1
    
    sorted_changes = dict(sorted(changes.items(), key=itemgetter(1), reverse=True))
    
    with open("tx_changes.json", "w") as file:
        json.dump(sorted_changes, file)
    print("Tx change file updated.")
    
    with open("files/chains_tx.json", "w") as file:
        json.dump(new_data, file)
    print("Tx file updated.")
    
    
compare_tx_number()


