import threading
import time
from api import get_bearer_token, save_bearer_token, renew_bearer_token, fetch_page
from utils import create_csv_writer
from config import NUM_PAGES, NUM_THREADS, API_URL
from curl_cffi import requests
from database import initialize_db, upsert_wallet

bearer_token = get_bearer_token()
bearer_token_lock = threading.Lock()  # Lock for synchronizing token renewal

headers = {
    'authorization': f'Bearer {bearer_token}',
    'user-agent': 'Mozilla/5.0'
}

def parse_body(body, writer, db_connection):
    for item in body['data']:
        address = item['wallet']['address']
        bot = item['wallet']['trading_bot']
        tags_list = [tag['tag'] for tag in item['wallet']['tags']]
        tags = ', '.join(tags_list)
        pnl_1d = item['pnl_1d']['pnl']
        roi_1d = item['pnl_1d']['roi']
        pnl_7d = item['pnl_7d']['pnl']
        roi_7d = item['pnl_7d']['roi']
        pnl_30d = item['pnl_30d']['pnl']
        roi_30d = item['pnl_30d']['roi']
        winrate = item['winrate']
        if winrate > 40:
            wallet_data = (address, roi_1d, pnl_1d, roi_7d, pnl_7d, roi_30d, pnl_30d, winrate, bot, tags)
            upsert_wallet(db_connection, wallet_data)
            writer.writerow(wallet_data)

def fetch_leaderboard_data(num_threads=NUM_THREADS):
    writer, file = create_csv_writer()
    start_time = time.time()

    def worker(page, thread_id, writer):
        global bearer_token
        db_connection = initialize_db()  # Create a connection for this thread
        max_retries = 50  # Maximum number of retries
        retries = 0
        while retries < max_retries:
            try:
                params = {'type': 'solana', 'page': str(page)}
                headers['authorization'] = f'Bearer {bearer_token}'
                response = fetch_page(page, db_connection, writer, headers, params)
                
                if response.status_code == 401:
                    # Re-check and renew token inside the lock
                    with bearer_token_lock:
                        current_bearer_token = get_bearer_token()  # Read file token inside the lock
                        if current_bearer_token == bearer_token:
                            print(f'Thread {thread_id} - Renewing token...')
                            new_token = renew_bearer_token(bearer_token)
                            bearer_token = new_token
                            save_bearer_token(new_token)
                            headers['authorization'] = f'Bearer {bearer_token}'
                            print(f"Bearer token renewed by Thread {thread_id}: {bearer_token}")
                            
                elif response.status_code == 429:
                    wait_time = 10
                    rate_limit_reset = int(response.headers.get('X-Rate-Limit-Reset'))
                    current_time = int(time.time())
                    wait_time = rate_limit_reset - current_time
                    print(f'Thread {thread_id} - Page {page}: Rate limited. Waiting for {wait_time} seconds.')
                    time.sleep(wait_time)
                else:
                    print(f'Thread {thread_id} - Page {page}: {response.status_code}')
                    parse_body(response.json(), writer, db_connection)  # Pass thread’s connection
                    break
            except requests.exceptions.Timeout:
                retries += 1
                if retries == 10:
                    print(f'Thread {thread_id} - Page {page}: 10 retries reached. Cold stopping for 2 minutes.')
                    time.sleep(120)  # Cold stop for 2 minutes
                elif retries == 20:
                    print(f'Thread {thread_id} - Page {page}: 20 retries reached. Cold stopping for 4 minutes.')
                    time.sleep(240)  # Cold stop for 4 minutes
                else:
                    wait_time = retries * 5  # Exponential backoff
                    print(f'Thread {thread_id} - Page {page}: Timeout. Retrying in {wait_time} seconds. (Attempt {retries}/{max_retries})')
                    time.sleep(wait_time)
            except Exception as e:
                print(f'Thread {thread_id} - Page {page}: Exception: {str(e)}')
                retries += 1
                if retries == 10:
                    print(f'Thread {thread_id} - Page {page}: 10 retries reached. Cold stopping for 2 minutes.')
                    time.sleep(120)  # Cold stop for 2 minutes
                elif retries == 20:
                    print(f'Thread {thread_id} - Page {page}: 20 retries reached. Cold stopping for 4 minutes.')
                    time.sleep(240)  # Cold stop for 4 minutes
                else:
                    wait_time = retries * 5  # Exponential backoff
                    print(f'Thread {thread_id} - Page {page}: Retrying in {wait_time} seconds. (Attempt {retries}/{max_retries})')
                    time.sleep(wait_time)

        db_connection.close()  # Close the connection after processing

    threads = []
    for i in range(num_threads):
        for page in range(i + 1, NUM_PAGES + 1, num_threads):
            thread = threading.Thread(target=worker, args=(page, i + 1, writer))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    file.close()
    print(f"Total time taken: {time.time() - start_time} seconds")

fetch_leaderboard_data()