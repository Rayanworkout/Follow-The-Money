import requests
from os import path
import json
from operator import itemgetter
# import web3

# https://web3py.readthedocs.io/en/stable/web3.main.html

def tvl_gainer():
    """Fetching TVL evolution of chains"""
    # Compute % change of the chain's TVL
    variation = lambda x, y: round((x - y) / y * 100, 2)
   
    if path.exists("TVLS.json"):
    
        # Getting old TVL data
        with open("TVLS.json") as file:
            old_data = json.load(file)
    
        # Fetching fresh data (chain, TVL)
        res = requests.get("https://api.llama.fi/chains").json()
        new_data = dict([(c["name"], round(c["tvl"], 2)) for c in res if c["name"] in old_data])
        
        # Comparing (applying variation func to each chain then sorting result)
        changes = dict([(chain, variation(new_data[chain], old_data[chain])) for chain in new_data 
                        if variation(new_data[chain], old_data[chain]) > 0])
        
        sorted_changes = sorted(changes.items(), key=itemgetter(1), reverse=True)
        
        with open("TVLS.json", "w") as file:
            json.dump(dict(sorted_changes), file)
    
    # Update the file
    with open("TVLS.json", "w") as file:
        res = requests.get("https://api.llama.fi/chains").json()
        json.dump(dict([(c["name"], round(c["tvl"], 2)) for c in res if c["tvl"] > 0]), file)
    print("File updated.")
    
        
# tvl_gainer()
