import os
from pathlib import Path

# Ensure tests import the Settings class fresh
os.environ.pop('DATABASE_URL', None)

from app.core.config import Settings


def test_default_database_url_is_absolute():
    s = Settings()
    assert s.DATABASE_URL.startswith('sqlite:///')
    # path after sqlite:/// should be absolute
    path_part = s.DATABASE_URL[len('sqlite:///'):]
    assert Path(path_part).is_absolute()


def test_normalize_relative_sqlite_env(tmp_path, monkeypatch):
    # Create a dummy relative path like ./clinic_billing.db
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///./clinic_billing.db')
    s = Settings()
    path_part = s.DATABASE_URL[len('sqlite:///'):]
    p = Path(path_part).resolve()
    assert p.is_absolute()
    # And it should be inside the backend directory
    backend_dir = Path(__file__).resolve().parents[2].resolve()
    # Use is_relative_to for a robust cross-platform check
    assert p.is_relative_to(backend_dir)
