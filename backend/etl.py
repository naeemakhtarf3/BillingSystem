import argparse
from datetime import datetime

from app.services.etl_service import ETLService
from app.models.etl_status import ETLProcessStatus
from app.db.session import SessionLocal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ETL aggregation for reports")
    parser.add_argument("--from", dest="from_date", help="Start date YYYY-MM-DD", required=False)
    parser.add_argument("--to", dest="to_date", help="End date YYYY-MM-DD", required=False)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    from_date = datetime.fromisoformat(args.from_date) if args.from_date else None
    to_date = datetime.fromisoformat(args.to_date) if args.to_date else None

    etl_service = ETLService()
    # Track status for observability
    with SessionLocal() as db:
        status = ETLProcessStatus(process_name="etl_reports", status="running")
        db.add(status)
        db.commit()
        try:
            etl_service.run_for_range(from_date=from_date, to_date=to_date)
            status.status = "completed"
            db.commit()
        except Exception as e:
            status.status = "failed"
            status.error_message = str(e)
            db.commit()
            raise


if __name__ == "__main__":
    main()


