import sqlite3
from category import category_mapping

conn = sqlite3.connect('category_mapping.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS mapping
              (category text PRIMARY KEY, codes text)''')

for category, codes in category_mapping.items():
    codes_str = ','.join(codes)
    c.execute("INSERT INTO mapping (category, codes) VALUES (?, ?)", (category, codes_str))

conn.commit()
conn.close()
