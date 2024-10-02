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

def get_native_coin_balance(api_key, address, chain_url):
    params = {
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': api_key
    }
    response = requests.get(chain_url, params=params)
    data = response.json()
    if 'result' in data:
        balance = int(data['result']) / 10**18
        return balance
    else:
        return 0


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

    # Sắp xếp các token theo thời gian giao dịch gần nhất (timeStamp)
    sorted_tokens = sorted(tokens, key=lambda x: int(x['timeStamp']), reverse=True)

    token_balances = {}
    unique_tokens = set()
    for token in sorted_tokens:
        token_address = token['contractAddress']
        if token_address in unique_tokens:
            continue
        unique_tokens.add(token_address)
        if len(unique_tokens) > token_limit:
            break
        token_symbol = token['tokenSymbol']
        token_balance = get_token_balance(api_key, address, token_address, chain_url)
        token_balances[token_symbol] = token_balance

    # Lấy số dư native coin (ví dụ ETH, BNB)
    native_coin_balance = get_native_coin_balance(api_key, address, chain_url)
    token_balances['Native Coin'] = native_coin_balance

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
    if 'result' in data:
        balance = int(data['result']) / 10**18
        return balance
    else:
        return 0

import requests

base_api_url = 'https://dapp.gateio.services/web3-bdm/web3-api/assetV2/getAssetNum'

# Hàm xử lý mỗi ví để lấy thông tin từ Gate.io API
def get_asset_data(wallet_address):
    # Tạo URL với ví EVM
    api_url = f"{base_api_url}?wallet_address=EVM:{wallet_address}"
    
    try:
        # Gửi yêu cầu GET tới API
        response = requests.get(api_url)
        
        # Kiểm tra nếu yêu cầu thành công (HTTP status code 200)
        if response.status_code == 200:
            # Phản hồi từ API (JSON)
            data = response.json()
            
            # Lấy giá trị token balance USD hoặc trả về 0.00 nếu không có
            token_balance_usd = data['data'].get('token_balance_usd', '0.00')
            return f"Phản hồi cho địa chỉ {wallet_address}: {token_balance_usd} USD"
        else:
            return f"Lỗi: Không thể kết nối tới API, mã lỗi {response.status_code} cho địa chỉ {wallet_address}"
    except Exception as e:
        return f"Lỗi khi gửi yêu cầu cho địa chỉ {wallet_address}: {e}"



'''base_api_url = 'https://dapp.gateio.services/web3-bdm/web3-api/assetV2/getAssetNum'
wallet_addresses = [
'0x891635785F3EF6d3c47a86f69DA62F226DFB967D',
'0xAb42449ea34524b85AA2502058856C45b9867E30'
    # Thêm các địa chỉ ví khác
]

import requests

base_api_url = 'https://dapp.gateio.services/web3-bdm/web3-api/assetV2/getAssetNum'

# Hàm xử lý mỗi ví để lấy thông tin từ Gate.io API
def get_asset_data(wallet_address):
    # Tạo URL với ví EVM
    api_url = f"{base_api_url}?wallet_address=EVM:{wallet_address}"
    
    try:
        # Gửi yêu cầu GET tới API
        response = requests.get(api_url)
        
        # Kiểm tra nếu yêu cầu thành công (HTTP status code 200)
        if response.status_code == 200:
            # Phản hồi từ API (JSON)
            data = response.json()
            
            # Lấy giá trị token balance USD hoặc trả về 0.00 nếu không có
            token_balance_usd = data['data'].get('token_balance_usd', '0.00')
            return f"Phản hồi cho địa chỉ {wallet_address}: {token_balance_usd} USD"
        else:
            return f"Lỗi: Không thể kết nối tới API, mã lỗi {response.status_code} cho địa chỉ {wallet_address}"
    except Exception as e:
        return f"Lỗi khi gửi yêu cầu cho địa chỉ {wallet_address}: {e}"
z
# Hàm xử lý mỗi ví
def get_asset_data(wallet_address):
    # Tạo URL với ví EVM
    api_url = f"{base_api_url}?wallet_address=EVM:{wallet_address}"
    
    try:
        # Gửi yêu cầu GET tới API
        response = requests.get(api_url)
        
        # Kiểm tra nếu yêu cầu thành công (HTTP status code 200)
        if response.status_code == 200:
            # Phản hồi từ API (JSON)
            data = response.json()
            
            # Xử lý dữ liệu hoặc in kết quả
            print(f"Phản hồi cho địa chỉ {wallet_address}:", data['data'].get('token_balance_usd', '0.00'))
        else:
            print(f"Lỗi: Không thể kết nối tới API, mã lỗi {response.status_code} cho địa chỉ {wallet_address}")
            
    except Exception as e:
        print(f"Lỗi khi gửi yêu cầu cho địa chỉ {wallet_address}: {e}")

# Lặp qua từng địa chỉ trong danh sách
for wallet in wallet_addresses:
    get_asset_data(wallet)
    
input()
'''