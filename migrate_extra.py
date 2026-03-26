import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'zomin_market.db')

def update_db():
    print("Database yangilanmoqda...")
    conn = sqlite3.connect(db_path)
    
    # Check if 'views' exists
    try:
        conn.execute('ALTER TABLE listings ADD COLUMN views INTEGER DEFAULT 0')
        print("'views' ustuni qo'shildi.")
    except sqlite3.OperationalError as e:
        print(e)
        
    # Check if 'condition' exists
    try:
        conn.execute('ALTER TABLE listings ADD COLUMN condition TEXT DEFAULT "Noma''lum"')
        print("'condition' ustuni qo'shildi.")
    except sqlite3.OperationalError as e:
        print(e)
        
    conn.commit()
    conn.close()
    print("Muvaffaqiyatli!")

if __name__ == '__main__':
    update_db()
