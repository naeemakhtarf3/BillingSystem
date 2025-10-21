const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchRevenue(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/revenue?${query}`, { headers: { Accept: 'application/json' } });
  return res.json();
}

export async function fetchPatientHistory(patientId, params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/patients/${patientId}/history?${query}`, { headers: { Accept: 'application/json' } });
  return res.json();
}

export async function fetchOutstanding(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/outstanding?${query}`, { headers: { Accept: 'application/json' } });
  return res.json();
}


