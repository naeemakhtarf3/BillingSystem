"""
Transaction management for atomic operations.

This module provides transaction decorators and context managers
for ensuring atomic operations in the patient admission workflow.
"""

from functools import wraps
from typing import Callable, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import SessionLocal
from app.core.exceptions import ConcurrencyException, AdmissionWorkflowException
import logging

logger = logging.getLogger(__name__)

class TransactionManager:
    """Context manager for database transactions."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self._should_close = db is None
    
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback on exception
            self.db.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            # Commit on success
            try:
                self.db.commit()
                logger.debug("Transaction committed successfully")
            except SQLAlchemyError as e:
                self.db.rollback()
                logger.error(f"Transaction commit failed, rolled back: {e}")
                raise
        
        if self._should_close:
            self.db.close()

def atomic_operation(func: Callable) -> Callable:
    """Decorator for atomic database operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = None
        
        # Find database session in arguments
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if not db:
            # Create new session if none provided
            db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            with TransactionManager(db):
                result = func(*args, **kwargs)
                return result
        except Exception as e:
            logger.error(f"Atomic operation failed: {e}")
            raise
        finally:
            if should_close and db:
                db.close()
    
    return wrapper

def atomic_admission_operation(func: Callable) -> Callable:
    """Decorator for atomic admission operations with concurrency control."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = None
        
        # Find database session in arguments
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if not db:
            db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            with TransactionManager(db):
                # Add optimistic locking check
                result = func(*args, **kwargs)
                return result
        except SQLAlchemyError as e:
            if "version" in str(e).lower() or "concurrent" in str(e).lower():
                raise ConcurrencyException(
                    resource_id=getattr(args[0], 'id', 0) if args else 0,
                    message="Concurrent modification detected"
                )
            raise
        except Exception as e:
            logger.error(f"Atomic admission operation failed: {e}")
            raise
        finally:
            if should_close and db:
                db.close()
    
    return wrapper

def with_retry(max_retries: int = 3, delay: float = 0.1):
    """Decorator for retrying operations on concurrency conflicts."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ConcurrencyException as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Concurrency conflict, retrying ({attempt + 1}/{max_retries}): {e}")
                        import time
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"Max retries exceeded for concurrency conflict: {e}")
                        raise
                except Exception as e:
                    # Don't retry on other exceptions
                    raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

class OptimisticLockingMixin:
    """Mixin for optimistic locking support."""
    
    def check_version(self, db: Session, model_class, record_id: int, expected_version: int) -> bool:
        """Check if record version matches expected version."""
        try:
            record = db.query(model_class).filter(model_class.id == record_id).first()
            if not record:
                return False
            
            current_version = getattr(record, 'version', 0)
            return current_version == expected_version
        except Exception as e:
            logger.error(f"Version check failed: {e}")
            return False
    
    def increment_version(self, db: Session, model_class, record_id: int) -> bool:
        """Increment record version for optimistic locking."""
        try:
            record = db.query(model_class).filter(model_class.id == record_id).first()
            if not record:
                return False
            
            current_version = getattr(record, 'version', 0)
            setattr(record, 'version', current_version + 1)
            db.add(record)
            return True
        except Exception as e:
            logger.error(f"Version increment failed: {e}")
            return False

def ensure_atomic_admission(func: Callable) -> Callable:
    """Decorator for ensuring atomic admission operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = None
        
        # Find database session in arguments
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if not db:
            db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            with TransactionManager(db):
                # Ensure we're in a transaction
                if not db.in_transaction():
                    raise AdmissionWorkflowException(
                        "Database transaction not available",
                        "TRANSACTION_ERROR"
                    )
                
                result = func(*args, **kwargs)
                return result
        except Exception as e:
            logger.error(f"Atomic admission operation failed: {e}")
            raise
        finally:
            if should_close and db:
                db.close()
    
    return wrapper

def rollback_on_exception(func: Callable) -> Callable:
    """Decorator that ensures rollback on any exception."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = None
        
        # Find database session in arguments
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if not db:
            db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Operation failed, transaction rolled back: {e}")
            raise
        finally:
            if should_close and db:
                db.close()
    
    return wrapper
