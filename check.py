import sqlite3

DB_FILE = "bloodbankdb.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("SELECT * FROM donors")
donors = cursor.fetchall()

print("Donors List:")
for donor in donors:
    print(donor)

conn.close()
