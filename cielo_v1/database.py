import sqlite3

def initialize_db(db_name='wallets.db'):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            address TEXT PRIMARY KEY,
            roi_1d REAL,
            pnl_1d REAL,
            roi_7d REAL,
            pnl_7d REAL,
            roi_30d REAL,
            pnl_30d REAL,
            winrate REAL,
            bot TEXT,
            tags TEXT
        )
    ''')
    connection.commit()
    return connection

def upsert_wallet(connection, wallet_data):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO wallets 
        (address, roi_1d, pnl_1d, roi_7d, pnl_7d, roi_30d, pnl_30d, winrate, bot, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(address) DO UPDATE SET
        roi_1d=excluded.roi_1d,
        pnl_1d=excluded.pnl_1d,
        roi_7d=excluded.roi_7d,
        pnl_7d=excluded.pnl_7d,
        roi_30d=excluded.roi_30d,
        pnl_30d=excluded.pnl_30d,
        winrate=excluded.winrate,
        bot=excluded.bot,
        tags=excluded.tags
    ''', wallet_data)
    connection.commit()