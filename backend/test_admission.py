from app.db.session import get_db
from app.services.admission_service import AdmissionService
from app.models.admission import AdmissionStatus

db = next(get_db())
service = AdmissionService(db)

print('Testing get_admissions method...')
try:
    result = service.get_admissions(status=AdmissionStatus.ACTIVE, skip=0, limit=10)
    print(f'Success: Found {len(result)} active admissions')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
