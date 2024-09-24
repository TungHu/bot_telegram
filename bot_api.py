import requests
from config import ARBISCAN_API_KEY, ETHERSCAN_API_KEY, BSCSCAN_API_KEY, OPTIMISM_API_KEY, POLYGON_API_KEY, BASE_API_KEY

chain_apis = {
    'ethereum': {
        'url': 'https://api.etherscan.io/api',
        'api_key': ETHERSCAN_API_KEY  # Thay thế bằng API key của bạn
    },
    'bsc': {
        'url': 'https://api.bscscan.com/api',
        'api_key': BSCSCAN_API_KEY
    },
    'arbitrum': {
        'url': 'https://api.arbiscan.io/api',
        'api_key': ARBISCAN_API_KEY
    },
    'polygon': {
        'url': 'https://api.polygonscan.com/api',
        'api_key': POLYGON_API_KEY
    },
    'optimism': {
        'url': 'https://api-optimistic.etherscan.io/api',
        'api_key': OPTIMISM_API_KEY
    },
    'base': {
        'url': 'https://api.basescan.org/api',
        'api_key': BASE_API_KEY
    }
}


def get_token_balances(api_key, address, chain_url, token_limit=5):
    url = chain_url

    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'apikey': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()
    tokens = data.get('result', [])

    token_balances = {}
    unique_tokens = set()
    for token in tokens:
        token_address = token['contractAddress']
        if token_address in unique_tokens:
            continue
        unique_tokens.add(token_address)
        if len(unique_tokens) > token_limit:
            break
        token_symbol = token['tokenSymbol']
        token_balance = get_token_balance(api_key, address, token_address, chain_url)
        token_balances[token_symbol] = token_balance

    return token_balances

def get_token_balance(api_key, address, token_address, chain_url):
    url = chain_url

    params = {
        'module': 'account',
        'action': 'tokenbalance',
        'contractaddress': token_address,
        'address': address,
        'tag': 'latest',
        'apikey': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()
    balance = int(data['result']) / 10**18
    return balance
