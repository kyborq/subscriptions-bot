from datetime import datetime, timedelta
import sqlite3


def init_db():
  conn = sqlite3.connect('subscriptions.db')
  cursor = conn.cursor()
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER UNIQUE NOT NULL,
      subscription_start_date TEXT,
      subscription_end_date TEXT
    )
  ''')
  conn.commit()
  conn.close()

def add_subscription(user_id):
  conn = sqlite3.connect('subscriptions.db')
  cursor = conn.cursor()

  start_date = datetime.now().strftime('%Y-%m-%d')
  end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
  
  cursor.execute('''
    INSERT INTO subscriptions (user_id, subscription_start_date, subscription_end_date)
    VALUES (?, ?, ?)
  ''', (user_id, start_date, end_date))

  conn.commit()
  conn.close()

def renew_subscription(user_id):
  conn = sqlite3.connect('subscriptions.db')
  cursor = conn.cursor()
  
  cursor.execute('''
    SELECT subscription_end_date
    FROM subscriptions
    WHERE user_id = ?
  ''', (user_id,))
  result = cursor.fetchone()
  
  if result:
    new_start_date = datetime.now().strftime('%Y-%m-%d')
    new_start_date_obj = datetime.strptime(new_start_date, '%Y-%m-%d')
    new_end_date = (new_start_date_obj + timedelta(days=30)).strftime('%Y-%m-%d')
    
    cursor.execute('''
      UPDATE subscriptions
      SET subscription_start_date = ?, subscription_end_date = ?
      WHERE user_id = ?
    ''', (new_start_date, new_end_date, user_id))
    
    conn.commit()
  
  conn.close()


def check_subscription(user_id):
  conn = sqlite3.connect('subscriptions.db')
  cursor = conn.cursor()

  cursor.execute('''
    SELECT subscription_start_date, subscription_end_date
    FROM subscriptions
    WHERE user_id = ?
  ''', (user_id,))

  result = cursor.fetchone()
  conn.close()
  return result