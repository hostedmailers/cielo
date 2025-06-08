import csv
from datetime import datetime

def create_csv_writer():
    filename = f'dev/wallets_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
    file = open(filename, mode='w', newline='')
    writer = csv.writer(file)
    writer.writerow(['Address', 'ROI 1D', 'PNL 1D', 'ROI 7D', 'PNL 7D', 'ROI 30D', 'PNL 30D', 'WINRATE', 'BOT', 'TAGS'])
    return writer, file