#!/usr/bin/env python3
"""
ID mapping utilities for converting between integer IDs and UUIDs
"""

import sqlite3
from typing import Optional, Dict, Any

def get_patient_uuid_by_id(patient_id: int) -> Optional[str]:
    """
    Get patient UUID by integer ID.
    
    Args:
        patient_id: Integer patient ID
        
    Returns:
        Patient UUID string or None if not found
    """
    conn = sqlite3.connect('clinic_billing.db')
    cursor = conn.cursor()
    
    try:
        # Get all patients and map by index
        cursor.execute('SELECT id FROM patients ORDER BY created_at')
        patients = cursor.fetchall()
        
        if 1 <= patient_id <= len(patients):
            return patients[patient_id - 1][0]  # Convert to 0-based index
        return None
    finally:
        conn.close()

def get_staff_uuid_by_id(staff_id: int) -> Optional[str]:
    """
    Get staff UUID by integer ID.
    
    Args:
        staff_id: Integer staff ID
        
    Returns:
        Staff UUID string or None if not found
    """
    conn = sqlite3.connect('clinic_billing.db')
    cursor = conn.cursor()
    
    try:
        # Get all staff and map by index
        cursor.execute('SELECT id FROM staff ORDER BY created_at')
        staff = cursor.fetchall()
        
        if 1 <= staff_id <= len(staff):
            return staff[staff_id - 1][0]  # Convert to 0-based index
        return None
    finally:
        conn.close()

def map_request_ids(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map integer IDs to UUIDs in request data.
    
    Args:
        request_data: Request data dictionary
        
    Returns:
        Updated request data with UUIDs
    """
    mapped_data = request_data.copy()
    
    # Map patient_id if it's an integer
    if 'patient_id' in mapped_data and isinstance(mapped_data['patient_id'], int):
        patient_uuid = get_patient_uuid_by_id(mapped_data['patient_id'])
        if patient_uuid:
            mapped_data['patient_id'] = patient_uuid
        else:
            raise ValueError(f"Patient ID {mapped_data['patient_id']} not found")
    
    # Map staff_id if it's an integer
    if 'staff_id' in mapped_data and isinstance(mapped_data['staff_id'], int):
        staff_uuid = get_staff_uuid_by_id(mapped_data['staff_id'])
        if staff_uuid:
            mapped_data['staff_id'] = staff_uuid
        else:
            raise ValueError(f"Staff ID {mapped_data['staff_id']} not found")
    
    return mapped_data
