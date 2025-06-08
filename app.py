from curl_cffi import requests
import threading
import time
import csv
from datetime import datetime
from db import check_db_connectivity, initialize_firebase


db = initialize_firebase()
if db is None or not check_db_connectivity(db):
    raise Exception("Initialization failed. Cannot proceed without a database connection.")

from bearer import renew_bearer_token

def get_bearer_token():
    with open('bearer_token.txt', 'r') as file:
        return file.read().strip()

def save_bearer_token(token):
    with open('bearer_token.txt', 'w') as file:
        file.write(token)

bearer_token = get_bearer_token()

def parse_body(body, writer):
    counter = 1  
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
        if winrate>40:
                # doc_ref = db.collection('wallets').document(address)
                # doc = doc_ref.get()
                # if doc.exists:
                #     print(f"{counter}. Document for {address} already existed and will be updated.")
                #     counter += 1  # Increment the counter
                # else:
                #     print(f"Document for {address} does not exist and will be created.")
                # doc_ref.set({
                #     'roi_1d': roi_1d,
                #     'pnl_1d': pnl_1d,
                #     'roi_7d': roi_7d,
                #     'pnl_7d': pnl_7d,
                #     'roi_30d': roi_30d,
                #     'pnl_30d': pnl_30d,
                #     'winrate': winrate,
                #     'bot': bot,
                #     'tags': tags
                # }, merge=True)
                writer.writerow([address, roi_1d, pnl_1d, roi_7d, pnl_7d, roi_30d, pnl_30d, winrate, bot, tags])  # Write the data row

def fetch_leaderboard_data(num_threads=10):
    start_time = time.time()  # Record the start time
    def fetch_page(page, thread_id, writer):
        global bearer_token
        max_retries = 50  # Maximum number of retries
        retries = 0
        while retries < max_retries:
            try:
                headers = {
                    'authorization': f'Bearer {bearer_token}',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
                }
                params = {
                    'type': 'solana',
                    'page': str(page),
                }

                response = requests.get('https://feed-api.cielo.finance/v1/leaderboard/tag', params=params, headers=headers)
                if response.status_code == 401:
                    print(f'Thread {thread_id} - Page {page}: Unauthorized. Renewing token.')
                    new_token = renew_bearer_token(bearer_token)
                    bearer_token = new_token
                    save_bearer_token(new_token)
                    # renew_bearer_token(bearer_token)
                if response.status_code == 429:
                    print(f'429 RATE LIMITEDDDD : {response.headers}')
                    # wait_time = random.randint(5, 10)
                    # print(f'Thread {thread_id} - Page {page}: Rate limited. Waiting for {wait_time} seconds.')
                    rate_limit_reset = int(response.headers.get('X-Rate-Limit-Reset'))
                    current_time = int(time.time())
                    wait_time = rate_limit_reset - current_time
                    print(f'Thread {thread_id} - Page {page}: Rate limited. Waiting for {wait_time} seconds.')
                    time.sleep(wait_time)
                else:
                    print(f'Thread {thread_id} - Page {page}: {response.status_code}')
                    # print(response.headers)
                    parse_body(response.json(), writer)
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


    filename = 'dev/wallets_' +datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Address', 'ROI 1D', 'PNL 1D' ,'ROI 7D', 'PNL 7D' , 'ROI 30D', 'PNL 30D', 'WINRATE', 'BOT', 'TAGS'])  # Write the header

        threads = []
        for i in range(num_threads):
            for page in range(i + 1, 12, num_threads):  # Adjust the range as needed
                thread = threading.Thread(target=fetch_page, args=(page, i + 1, writer))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    end_time = time.time()  # Record the end time
    print(f"Total time taken: {end_time - start_time} seconds")


fetch_leaderboard_data()