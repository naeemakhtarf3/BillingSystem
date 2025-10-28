import sqlite3

conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()

# Create rooms table
cursor.execute('''
CREATE TABLE IF NOT EXISTS room (
    id INTEGER NOT NULL,
    room_number VARCHAR NOT NULL,
    type VARCHAR(8) NOT NULL CHECK (type IN ('standard', 'private', 'icu')),
    status VARCHAR(11) NOT NULL CHECK (status IN ('available', 'occupied', 'maintenance')),
    daily_rate_cents INTEGER NOT NULL,
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    PRIMARY KEY (id)
)
''')

# Create admission table
cursor.execute('''
CREATE TABLE IF NOT EXISTS admission (
    id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    patient_id VARCHAR NOT NULL,
    staff_id VARCHAR NOT NULL,
    admission_date DATETIME NOT NULL,
    discharge_date DATETIME,
    discharge_reason VARCHAR,
    discharge_notes TEXT,
    invoice_id INTEGER,
    status VARCHAR(10) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'discharged')),
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    version INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    FOREIGN KEY(room_id) REFERENCES room (id)
)
''')

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS ix_room_id ON room (id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_room_room_number ON room (room_number)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_id ON admission (id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_room_id ON admission (room_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_patient_id ON admission (patient_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_staff_id ON admission (staff_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_admission_date ON admission (admission_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_discharge_date ON admission (discharge_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_discharge_reason ON admission (discharge_reason)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_invoice_id ON admission (invoice_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_status ON admission (status)')

# Insert some sample rooms
cursor.execute('''
INSERT OR IGNORE INTO room (id, room_number, type, status, daily_rate_cents) VALUES
(1, '101A', 'standard', 'available', 15000),
(2, '102A', 'standard', 'available', 15000),
(3, '201A', 'private', 'available', 25000),
(4, '202A', 'private', 'available', 25000),
(5, '301A', 'icu', 'available', 50000)
''')

conn.commit()
conn.close()

print("Tables created successfully!")
