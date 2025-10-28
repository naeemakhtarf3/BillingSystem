import sqlite3

conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()

# First, let's recreate the table with the correct constraint
cursor.execute('''
CREATE TABLE admission_new (
    id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    patient_id VARCHAR NOT NULL,
    staff_id VARCHAR NOT NULL,
    admission_date DATETIME NOT NULL,
    discharge_date DATETIME,
    discharge_reason VARCHAR,
    discharge_notes TEXT,
    invoice_id INTEGER,
    status VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'DISCHARGED')),
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    version INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    FOREIGN KEY(room_id) REFERENCES room (id)
)
''')

# Copy data from old table, converting status to uppercase
cursor.execute('''
INSERT INTO admission_new 
SELECT id, room_id, patient_id, staff_id, admission_date, discharge_date, 
       discharge_reason, discharge_notes, invoice_id, 
       CASE WHEN status = 'active' THEN 'ACTIVE' ELSE 'DISCHARGED' END,
       created_at, updated_at, version
FROM admission
''')

# Drop old table and rename new one
cursor.execute('DROP TABLE admission')
cursor.execute('ALTER TABLE admission_new RENAME TO admission')

# Recreate indexes
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_id ON admission (id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_room_id ON admission (room_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_patient_id ON admission (patient_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_staff_id ON admission (staff_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_admission_date ON admission (admission_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_discharge_date ON admission (discharge_date)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_discharge_reason ON admission (discharge_reason)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_invoice_id ON admission (invoice_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS ix_admission_status ON admission (status)')

conn.commit()

# Verify the change
cursor.execute('SELECT * FROM admission')
admission = cursor.fetchone()
print(f"Updated admission: {admission}")

conn.close()
print("Admission table updated successfully!")