import sqlite3

conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()

# Update room types to uppercase
cursor.execute('UPDATE room SET type = ? WHERE type = ?', ('STANDARD', 'standard'))
cursor.execute('UPDATE room SET type = ? WHERE type = ?', ('PRIVATE', 'private'))
cursor.execute('UPDATE room SET type = ? WHERE type = ?', ('ICU', 'icu'))

# Update room status to uppercase
cursor.execute('UPDATE room SET status = ? WHERE status = ?', ('AVAILABLE', 'available'))
cursor.execute('UPDATE room SET status = ? WHERE status = ?', ('OCCUPIED', 'occupied'))
cursor.execute('UPDATE room SET status = ? WHERE status = ?', ('MAINTENANCE', 'maintenance'))

conn.commit()

# Verify the changes
cursor.execute('SELECT * FROM room')
rooms = cursor.fetchall()
print("Updated rooms:")
for room in rooms:
    print(f"  {room}")

conn.close()
print("Room table updated successfully!")
