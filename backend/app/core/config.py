from typing import List
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    def __init__(self):
        # Database
        # Default to a sqlite file located in the backend directory so that
        # scripts (create_sample_data.py) and the running server use the same DB
        # regardless of the current working directory.
        backend_dir = Path(__file__).resolve().parents[2]
        default_db_path = (backend_dir / "clinic_billing.db").as_posix()
        default_db_url = f"sqlite:///{default_db_path}"

        # Allow DATABASE_URL override from env, but if it's a sqlite URL with a
        # relative path (e.g. sqlite:///./clinic_billing.db) normalize it to an
        # absolute path inside the backend directory so all scripts use the same
        # file regardless of the current working directory.
        env_db_url = "postgresql://neondb_owner:npg_Xzxog43QnSfN@ep-lively-lab-admvsm99-pooler.c-2.us-east-1.aws.neon.tech/billingdb1?sslmode=require&channel_binding=require"
        if env_db_url:
            if env_db_url.startswith("sqlite:///"):
                # Extract the path portion after sqlite:///
                path_part = env_db_url[len("sqlite:///"):]
                # If it's a relative path (starts with ./ or doesn't start with /),
                # resolve it against backend_dir
                if path_part.startswith("./") or not Path(path_part).is_absolute():
                    abs_path = (backend_dir / Path(path_part)).resolve().as_posix()
                    env_db_url = f"sqlite:///{abs_path}"
            self.DATABASE_URL: str = env_db_url
        else:
            self.DATABASE_URL: str = default_db_url

        # JWT
        self.JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        # Stripe
        self.STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_51SDKdvI0OwBnbEX2nzwEPTIE1xscwZEZoJbluvX4hncILO1HxrSdy6WdM8Cwkw7MgJfHjmMWgCKfDdq0Tu4xhrpt00kN5PtJJ9")
        self.STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_51SDKdvI0OwBnbEX2mtaeqBTQmpfhnV45MEpnGoJoGdDSbzjLQ7YYADvD2608oNArI600PFpvYmJkaErCbSWGmohY00NBNTSJ8Z")
        self.STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "sk_test_51SDKdvI0OwBnbEX2mtaeqBTQmpfhnV45MEpnGoJoGdDSbzjLQ7YYADvD2608oNArI600PFpvYmJkaErCbSWGmohY00NBNTSJ8Z")

        # Application
        self.APP_NAME: str = os.getenv("APP_NAME", "Clinic Billing System")
        self.APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
        self.API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
        self.CORS_ORIGINS: List[str] = [x.strip() for x in "https://billingsystem-gm9s.onrender.com, http://localhost:5173,http://localhost:5174,http://localhost:8080,http://localhost:3001,http://127.0.0.1:5174,http://127.0.0.1:3000".split(",")]

        # Email Configuration
        self.MAIL_PROVIDER: str = os.getenv("MAIL_PROVIDER", "smtp")
        self.SMTP_HOST: str = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "2bef4f6fbd5c61")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "162ce783b1f47d")
        self.EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "no-reply@clinic.com")
        self.SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")

        # Google AI Configuration
        self.GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "AIzaSyDi0QD7_-N7JJFXm5B6wbhkXXJdnT_hKZo")

settings = Settings()
