import sqlite3
from datetime import datetime

conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()

# Create a new test admission
admission_data = {
    'room_id': 2,  # Use room 2 which is available
    'patient_id': 'PATIENT-002',
    'staff_id': 'STAFF-001',
    'admission_date': datetime.now().isoformat(),
    'status': 'ACTIVE'
}

cursor.execute('''
INSERT INTO admission (room_id, patient_id, staff_id, admission_date, status)
VALUES (?, ?, ?, ?, ?)
''', (
    admission_data['room_id'],
    admission_data['patient_id'],
    admission_data['staff_id'],
    admission_data['admission_date'],
    admission_data['status']
))

# Update room status to occupied
cursor.execute('UPDATE room SET status = ? WHERE id = ?', ('OCCUPIED', admission_data['room_id']))

conn.commit()

# Get the created admission
cursor.execute('SELECT * FROM admission WHERE patient_id = ?', (admission_data['patient_id'],))
admission = cursor.fetchone()
print(f"Created new admission: {admission}")

conn.close()
print("New test admission created successfully!")
