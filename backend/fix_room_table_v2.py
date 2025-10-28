import sqlite3

conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()

# Create new room table with correct constraints
cursor.execute('''
CREATE TABLE room_new (
    id INTEGER NOT NULL,
    room_number VARCHAR NOT NULL,
    type VARCHAR(8) NOT NULL CHECK (type IN ('STANDARD', 'PRIVATE', 'ICU')),
    status VARCHAR(11) NOT NULL CHECK (status IN ('AVAILABLE', 'OCCUPIED', 'MAINTENANCE')),
    daily_rate_cents INTEGER NOT NULL,
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    version INTEGER DEFAULT 1,
    PRIMARY KEY (id)
)
''')

# Copy data from old table, converting to uppercase
cursor.execute('''
INSERT INTO room_new 
SELECT id, room_number, 
       CASE 
         WHEN type = 'standard' THEN 'STANDARD'
         WHEN type = 'private' THEN 'PRIVATE'
         WHEN type = 'icu' THEN 'ICU'
         ELSE type
       END,
       CASE 
         WHEN status = 'available' THEN 'AVAILABLE'
         WHEN status = 'occupied' THEN 'OCCUPIED'
         WHEN status = 'maintenance' THEN 'MAINTENANCE'
         ELSE status
       END,
       daily_rate_cents, created_at, updated_at, version
FROM room
''')

# Drop old table and rename new one
cursor.execute('DROP TABLE room')
cursor.execute('ALTER TABLE room_new RENAME TO room')

# Recreate indexes
cursor.execute('CREATE INDEX IF NOT EXISTS ix_room_id ON room (id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_room_room_number ON room (room_number)')

conn.commit()

# Verify the changes
cursor.execute('SELECT * FROM room')
rooms = cursor.fetchall()
print("Updated rooms:")
for room in rooms:
    print(f"  {room}")

conn.close()
print("Room table updated successfully!")
