import sqlite3
from datetime import datetime

conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()

# Delete any existing test admissions
cursor.execute('DELETE FROM admission WHERE patient_id LIKE "PATIENT-%"')
cursor.execute('UPDATE room SET status = "AVAILABLE" WHERE id IN (1, 2, 3, 4, 5)')

# Create a fresh test admission
admission_data = {
    'room_id': 3,  # Use room 3 which is available
    'patient_id': 'PATIENT-003',
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
print(f"Created fresh admission: {admission}")

conn.close()
print("Fresh test admission created successfully!")
