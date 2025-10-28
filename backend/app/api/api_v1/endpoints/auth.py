from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from app.db.session import get_db
from app.models.staff import Staff
from app.schemas.auth import Token, LoginRequest
from app.schemas.staff import StaffCreate, StaffResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token
from app.core.config import settings
import uuid

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_staff(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    staff_id: str = payload.get("sub")
    if staff_id is None:
        raise credentials_exception

    # JWT 'sub' is stored as string; our Staff.id column uses UUID(as_uuid=True).
    # Convert to uuid.UUID before querying so SQLAlchemy can bind the value
    try:
        staff_uuid = uuid.UUID(staff_id) if not isinstance(staff_id, uuid.UUID) else staff_id
    except (ValueError, TypeError):
        raise credentials_exception

    staff = db.query(Staff).filter(Staff.id == staff_uuid).first()
    if staff is None:
        raise credentials_exception
    
    return staff

@router.post("/register", response_model=StaffResponse)
def register_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_staff = db.query(Staff).filter(Staff.email == staff.email).first()
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new staff
    from app.core.security import get_password_hash
    hashed_password = get_password_hash(staff.password)
    
    db_staff = Staff(
        email=staff.email,
        password_hash=hashed_password,
        name=staff.name,
        role=staff.role
    )
    
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    
    return db_staff

@router.post("/login", response_model=Token)
async def login_staff(request: Request, db: Session = Depends(get_db)):
    # Support both JSON body and form-encoded (tests send form data)
    username = None
    password = None

    content_type = request.headers.get('content-type', '')
    if 'application/json' in content_type:
        body = await request.json()
        username = body.get('username')
        password = body.get('password')
    else:
        form = await request.form()
        username = form.get('username') or form.get('username')
        password = form.get('password') or form.get('password')

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username and password are required")

    staff = db.query(Staff).filter(Staff.email == username).first()

    if not staff or not verify_password(password, staff.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(staff.id), "role": staff.role.value},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(staff.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: dict = Body(...), db: Session = Depends(get_db)):
    # Expecting JSON body like { "refresh_token": "..." }
    token = refresh_token.get("refresh_token") if isinstance(refresh_token, dict) else None
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="refresh_token is required")

    payload = verify_token(token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    staff_id = payload.get("sub")
    try:
        staff_uuid = uuid.UUID(staff_id) if not isinstance(staff_id, uuid.UUID) else staff_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Staff not found"
        )

    staff = db.query(Staff).filter(Staff.id == staff_uuid).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Staff not found"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(staff.id), "role": staff.role.value}, 
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": str(staff.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=StaffResponse)
def get_current_staff_info(current_staff: Staff = Depends(get_current_staff)):
    return current_staff

@router.get("/staff", response_model=List[StaffResponse])
def get_staff(db: Session = Depends(get_db), current_staff: Staff = Depends(get_current_staff)):
    staff = db.query(Staff).all()
    return staff

@router.get("/debug/staff")
def debug_staff(db: Session = Depends(get_db)):
    staff = db.query(Staff).all()
    return [{"email": s.email, "name": s.name, "role": s.role.value, "password_hash": s.password_hash} for s in staff]
