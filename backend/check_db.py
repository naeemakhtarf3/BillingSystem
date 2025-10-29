import sqlite3

conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Existing tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check if admission table exists
if ('admission',) in tables:
    print("\nAdmission table exists, checking structure:")
    cursor.execute("PRAGMA table_info(admission);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
else:
    print("\nAdmission table does not exist")

conn.close()
