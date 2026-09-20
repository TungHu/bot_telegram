# bot_telegram

Bot Telegram viết bằng Python dùng để kiểm tra số dư ví EVM: liệt kê token ERC-20 và native coin của danh sách ví trên 6 chain thông qua API Etherscan-style, đồng thời tra nhanh tổng giá trị token (USD) của ví qua API Gate.io. Toàn bộ chức năng chạy ở dạng hội thoại Telegram: chọn chain, dán danh sách ví, nhận kết quả.

## Tính năng

- Kiểm tra tối đa 5 token (theo giao dịch gần nhất) của mỗi ví, kèm số dư native coin.
- Nhập nhiều ví một lúc (mỗi dòng một địa chỉ).
- Tổng hợp kết quả cuối: số ví đã kiểm tra, số ví có token, tổng số dư theo từng token symbol.
- Hủy thao tác đang chạy bằng nút inline `Cancel` hoặc lệnh `/cancel`.
- Tra tổng giá trị token (USD) của ví EVM qua Gate.io, không cần API key.
- Hỗ trợ 6 chain: ethereum, bsc, arbitrum, polygon, optimism, base.
- Logging ra console (level INFO) để theo dõi tiến trình.

## Các chain hỗ trợ

| Chain | API endpoint | Biến API key trong `config.py` | chain_id |
|---|---|---|---|
| ethereum | `https://api.etherscan.io/api` | `ETHERSCAN_API_KEY` | 1 |
| bsc | `https://api.bscscan.com/api` | `BSCSCAN_API_KEY` | 56 |
| arbitrum | `https://api.arbiscan.io/api` | `ARBISCAN_API_KEY` | 42161 |
| polygon | `https://api.polygonscan.com/api` | `POLYGON_API_KEY` | 137 |
| optimism | `https://api-optimistic.etherscan.io/api` | `OPTIMISM_API_KEY` | 10 |
| base | `https://api.basescan.org/api` | `BASE_API_KEY` | 8453 |

Mỗi chain trong dict `chain_apis` (trong `bot_api.py`) gồm: `url`, `api_key`. Tên chain phải đúng như cột "Chain" vì code so khớp trực tiếp với key của dict.

> **Lưu ý:**
> - 6 endpoint trên thuộc **Etherscan API V1 và đã ngừng hoạt động từ 15/08/2025**, nên luồng kiểm tra token hiện tại có thể nhận lỗi từ API. Muốn dùng lại phải chuyển sang Etherscan API V2 `https://api.etherscan.io/v2/api?chainid=<chain_id>` (một key dùng chung cho mọi chain).
> - `get_asset_data` gọi endpoint riêng, không chính thức của Gate.io (`dapp.gateio.services/web3-bdm/web3-api/assetV2/getAssetNum`), không cần API key và có thể đổi/hỏng bất kỳ lúc nào.
> - `token_limit` mặc định là 5 token cho mỗi ví; token được chọn theo `timeStamp` giao dịch gần nhất nên ví có nhiều hơn 5 token sẽ không hiển thị hết.
> - Số dư token luôn chia cho `10**18`; token có `decimals` khác 18 (USDC/USDT 6 decimals, WBTC 8 decimals...) sẽ hiển thị sai đơn vị.
> - `requests` được gọi đồng bộ trong event loop async nên bot sẽ không phản hồi lệnh khác trong lúc đang kiểm tra; mỗi ví tốn tối đa khoảng 7 request HTTP.
> - Bot không xác thực người dùng - bất kỳ ai biết bot đều có thể kiểm tra ví. Xem mục "Bảo mật - đọc trước khi dùng".

## Yêu cầu

- Python 3.12 (đã kiểm thử với 3.12.6)
- Các thư viện trong `requirements.txt` (chính: `python-telegram-bot==21.5`, `requests==2.32.3`)
- Một bot Telegram và token lấy từ [@BotFather](https://t.me/BotFather)
- API key Etherscan-style cho mỗi chain muốn kiểm tra (etherscan.io, bscscan.com, arbiscan.io, polygonscan.com, optimistic.etherscan.io, basescan.org)

## Cài đặt

1. Clone repository:

```sh
git clone https://github.com/TungHu/bot_telegram.git
cd bot_telegram
```

2. Tạo môi trường ảo (khuyến nghị):

```sh
python -m venv env
```

Kích hoạt môi trường ảo:

```sh
# Windows (PowerShell / CMD)
env\Scripts\activate

# macOS / Linux
source env/bin/activate
```

3. Cài thư viện:

```sh
pip install -r requirements.txt
```

4. Tạo file `config.py` trong thư mục `bot_telegram` - **bắt buộc**, nếu thiếu bot sẽ báo `ModuleNotFoundError: No module named 'config'`:

```python
# config.py - File bí mật, KHÔNG commit lên Git (đã có trong .gitignore)
telegrambot_token = "1234567890:ABC..."   # Lấy từ @BotFather

ETHERSCAN_API_KEY = "..."   # https://etherscan.io/myapikey
BSCSCAN_API_KEY   = "..."   # https://bscscan.com/myapikey
ARBISCAN_API_KEY  = "..."   # https://arbiscan.io/myapikey
POLYGON_API_KEY   = "..."   # https://polygonscan.com/myapikey
OPTIMISM_API_KEY  = "..."   # https://optimistic.etherscan.io/myapikey
BASE_API_KEY      = "..."   # https://basescan.org/myapikey
```

5. (Tuỳ chọn) Mở thư mục bằng Visual Studio Code, hoặc mở bằng Visual Studio có cài Python workload.

## Cấu trúc dự án

```text
bot_telegram/
|-- bot_main.py        # Tầng bot: ConversationHandler, keyboard chọn chain, wallet_checker, cancel
|-- bot_api.py         # Tầng API: chain_apis + các hàm gọi Etherscan / Gate.io
|-- config.py          # (tự tạo) token bot + API key - KHÔNG commit
|-- requirements.txt
|-- .gitignore
`-- README.md
```

`config.py` không có trong repository và đã nằm trong `.gitignore` - **không** đưa file này lên Git.

## Hướng dẫn sử dụng

### 1. Chạy bot

```sh
python bot_main.py
```

Bot chạy ở chế độ polling và in log INFO ra console (`Chain selected by ...`, `Wallets input by ...`). Dừng bot bằng `Ctrl+C`.

### 2. Kiểm tra số dư token của danh sách ví trên một chain

Trong khung chat Telegram:

1. Gửi `/start`.
2. Bấm nút chain muốn kiểm tra (`ethereum`, `bsc`, `arbitrum`, `polygon`, `optimism`, `base`).
3. Dán danh sách ví, mỗi dòng một địa chỉ.
4. Bot gửi kết quả từng ví kèm nút `Cancel`, sau đó gửi phần tổng hợp.

```text
/start
-> Chọn chain bạn muốn kiểm tra hoặc chọn "get_asset_data" để lấy dữ liệu tài sản từ ví
click "Cancel" để dừng thao tác.

arbitrum
-> Vui lòng nhập các địa chỉ ví, mỗi ví trên một dòng:

0x891635785F3EF6d3c47a86f69DA62F226DFB967D
0xAb42449ea34524b85AA2502058856C45b9867E30
-> Ví 1/2: 0x891635785F3EF6d3c47a86f69DA62F226DFB967D
Token balances:
- USDT: 12.5
- Native Coin: 0.0311
-> Đã kiểm tra xong 2 ví.
2/2 ví có token.

Tổng token thu thập được:
- USDT: 12.5
- Native Coin: 0.0622
```

Mỗi ví được xử lý lần lượt, nghỉ 2 giây giữa các ví để tránh dồn request vào API.

### 3. Tra tổng giá trị tài sản (USD) qua Gate.io

Chọn `get_asset_data` ở bước 2 thay vì chọn chain, rồi dán danh sách ví. Bot trả về tổng giá trị token quy đổi USD của từng ví theo dữ liệu Gate.io.

```text
get_asset_data
-> Vui lòng nhập các địa chỉ ví, mỗi ví trên một dòng:

0x891635785F3EF6d3c47a86f69DA62F226DFB967D
-> Phản hồi cho địa chỉ 0x891635785F3EF6d3c47a86f69DA62F226DFB967D: 1234.56 USD
```

Chế độ này gọi API công khai của Gate.io nên kết quả **chỉ mang tính tham khảo**, không có nút `Cancel` và không có phần tổng hợp.

### 4. Hủy thao tác đang chạy

- Bấm nút inline `Cancel` dưới message kết quả, hoặc gửi lệnh `/cancel`.
- Bot đặt cờ `cancelled` trong `user_data` và gọi `cancel()` lên task kiểm tra ví, sau đó trả lời `Đã hủy bỏ thao tác.`
- Cờ chỉ được kiểm tra ở đầu mỗi vòng lặp ví, nên thao tác hủy có hiệu lực **sau khi ví đang xử lý xong**.

### 5. Nhập danh sách ví đúng định dạng

- Mỗi dòng một địa chỉ ví EVM (`0x...`).
- Dòng trắng bị bỏ qua, khoảng trắng đầu/cuối dòng được cắt bỏ.
- Code không validate định dạng ví, nên hãy kiểm tra địa chỉ đúng chuẩn checksum EIP-55 trước khi gửi.

### 6. Gọi trực tiếp các hàm trong `bot_api.py`

```python
from bot_api import chain_apis, get_token_balances, get_native_coin_balance, get_asset_data

chain = chain_apis['arbitrum']
address = "0x891635785F3EF6d3c47a86f69DA62F226DFB967D"

print(get_token_balances(chain['api_key'], address, chain['url']))       # dict token + Native Coin
print(get_native_coin_balance(chain['api_key'], address, chain['url']))  # chỉ số dư native coin
print(get_asset_data(address))                                          # tổng giá trị USD qua Gate.io
```

- `get_token_balances` trả về dict `{token_symbol: số_dư}` và luôn có thêm key `Native Coin`.
- `get_asset_data` không cần API key, trả về chuỗi đã format sẵn để gửi Telegram.

### 7. Log và debug

Bot dùng `logging.basicConfig(level=logging.INFO)` với format `%(asctime)s - %(name)s - %(levelname)s - %(message)s`. Khi cần xem chi tiết request/response, đổi tạm level thành `logging.DEBUG` lúc chạy cục bộ.

## Bảng tham chiếu hàm

| Hàm | Tham số | Ghi chú |
|---|---|---|
| `get_token_balances(api_key, address, chain_url, token_limit=5)` | `chain_url` lấy từ `chain_apis` | action `tokentx` -> lấy tối đa `token_limit` token unique mới nhất -> trả dict `{symbol: số_dư}` kèm key `Native Coin` |
| `get_token_balance(api_key, address, token_address, chain_url)` | | action `tokenbalance`, chia `10**18`; lỗi hoặc thiếu `result` -> trả `0` |
| `get_native_coin_balance(api_key, address, chain_url)` | | action `balance`, chia `10**18`; lỗi -> trả `0` |
| `get_asset_data(wallet_address)` | Địa chỉ ví EVM `0x...` | GET Gate.io `assetV2/getAssetNum`; trả chuỗi `"Phản hồi cho địa chỉ <ví>: <usd> USD"` |
| `wallet_checker(context, wallets, chain, api_key, chain_url, token_limit=5)` | Coroutine chạy nền | Gửi message từng ví kèm nút `Cancel`, nghỉ 2 giây/ví, rồi gửi phần tổng hợp |
| `start(update, context)` | Handler `/start` | Trả về state `CHAIN_SELECTION` |
| `chain_selection(update, context)` | State `CHAIN_SELECTION` | So khớp tên chain với `chain_apis`; sai thì yêu cầu chọn lại |
| `wallet_input(update, context)` | State `WALLET_INPUT` | Tách danh sách ví theo dòng, tạo task `wallet_checker` hoặc gọi `get_asset_data` |
| `cancel_callback(update, context)` | Nút inline `Cancel` | Đặt cờ `cancelled` và `task.cancel()` |
| `cancel(update, context)` | Handler `/cancel` | Như trên, dùng khi không có nút inline |

Các key lưu trong `context.user_data`: `chain`, `chat_id`, `wallet_task`, `cancelled`, `get_asset_data`.

## Bảo mật - đọc trước khi dùng

- **Không bao giờ commit `config.py`.** File này chứa bot token và 6 API key; đã được liệt kê trong `.gitignore`. Kiểm tra `git status` trước mỗi lần push.
- Bot token bị lộ coi như mất quyền điều khiển bot - vào `@BotFather` dùng `/revoke` để cấp token mới rồi cập nhật `config.py`.
- Etherscan-style API key bị lộ sẽ bị người khác dùng hết quota (free tier rất thấp) và request của bạn sẽ nhận `Max rate limit reached`.
- Bot **không giới hạn người dùng**: ai biết username bot cũng gửi được ví để query. Nếu triển khai công khai, hãy thêm whitelist `user_id` trước khi xử lý.
- Chỉ kiểm tra ví của bạn hoặc ví đã được chủ sở hữu cho phép; thu thập số dư ví của người khác có thể vi phạm pháp luật.
- Danh sách ví và kết quả truyền qua Telegram (không mã hoá đầu cuối), không phù hợp cho dữ liệu nhạy cảm.

## Lỗi thường gặp

| Lỗi | Nguyên nhân / cách xử lý |
|---|---|
| `ModuleNotFoundError: No module named 'config'` | Chưa tạo `config.py` hoặc chạy bot sai thư mục - xem bước 4 phần Cài đặt |
| `TelegramConflictError: terminated by other getUpdates request` | Bot đang chạy ở tiến trình/máy khác - mỗi token chỉ chạy 1 instance |
| `Chain không hợp lệ. Vui lòng chọn lại.` | Nhập tên chain sai; phải đúng một trong 6 giá trị trong bảng chain |
| `Không có token nào hoặc không lấy được thông tin.` | Ví chưa từng có giao dịch token, hoặc API trả lỗi/hết quota cho key đó |
| `NameError: name 'index' is not defined` | Danh sách ví rỗng (chỉ toàn dòng trắng) - phần tổng hợp dùng biến `index` chưa được gán |
| API trả `NOTOK` / `Max rate limit reached` | Vượt giới hạn ~5 request/giây của Etherscan free tier - giảm số ví mỗi lần hoặc nâng cấp key |
| API trả `Invalid API Key` / `Missing/Invalid API Key` | Key sai, dán thừa khoảng trắng, hoặc dùng key của chain khác với cột "Biến API key" |
| Bot im lặng sau khi gửi danh sách ví | `requests` đồng bộ đang chặn event loop; chờ ví hiện tại xong hoặc dùng `/cancel` |
| `pip install -r requirements.txt` lỗi ở `pywin32==306` | Package chỉ dành cho Windows; trên Linux/macOS cài tối thiểu `pip install python-telegram-bot==21.5 requests==2.32.3` |
| `requests.exceptions.ConnectionError` | Mất mạng, DNS bị chặn, hoặc API đổi domain (thường gặp với endpoint Gate.io) |

## Miễn trừ trách nhiệm

Dự án phục vụ mục đích học tập và nghiên cứu. Người dùng tự chịu trách nhiệm với mọi truy vấn dữ liệu ví, việc sử dụng bot token/API key của mình và việc tuân thủ pháp luật tại nơi mình sinh sống.
