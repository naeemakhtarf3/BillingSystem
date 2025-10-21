from __future__ import annotations

from datetime import datetime, date
from collections import defaultdict
from typing import Dict, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.mailer import get_mailer
from app.core.config import settings
from app.models.payment import Payment, PaymentStatus
from app.models.invoice import Invoice


class ETLService:
    """Service responsible for aggregating operational data into reporting schema.

    This scaffolding provides a stable API for CLI and scheduled runs.
    """

    def run_for_range(self, from_date: datetime | None, to_date: datetime | None) -> None:
        """Aggregate succeeded payments into revenue_metrics table per-day.

        This provides the minimal slice needed for US1 revenue charts.
        """
        with SessionLocal() as db:
            try:
                day_totals = self._extract_aggregate_payments_by_day(db, from_date, to_date)
                self._load_revenue_metrics(db, day_totals)
                # Populate patient payment history slice
                self._load_patient_payment_history(db, from_date, to_date)
                # Populate outstanding payments slice
                self._load_outstanding_payments(db)
            except Exception as e:
                # Stop processing and alert administrators
                try:
                    mailer = get_mailer()
                    mailer.send_email(
                        to=settings.EMAIL_FROM_ADDRESS,
                        subject="ETL Failure Alert",
                        body=f"ETL failed: {e}",
                    )
                except Exception:
                    pass
                raise

    def _extract_aggregate_payments_by_day(
        self, db: Session, from_date: datetime | None, to_date: datetime | None
    ) -> Dict[date, Tuple[float, int, float]]:
        query = db.query(Payment).filter(Payment.status == PaymentStatus.SUCCEEDED)
        if from_date:
            query = query.filter(Payment.received_at >= from_date)
        if to_date:
            query = query.filter(Payment.received_at <= to_date)

        buckets: Dict[date, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
        for p in query.all():
            day = p.received_at.date()
            total, count = buckets[day]
            total += (p.amount_cents or 0) / 100.0
            count += 1
            buckets[day] = (total, count)

        result: Dict[date, Tuple[float, int, float]] = {}
        for day, (total, count) in buckets.items():
            avg = (total / count) if count else 0.0
            result[day] = (total, count, avg)
        return result

    def _load_revenue_metrics(self, db: Session, day_totals: Dict[date, Tuple[float, int, float]]) -> None:
        if not day_totals:
            return
        min_day = min(day_totals.keys())
        max_day = max(day_totals.keys())
        # Upsert by deleting existing range then inserting fresh aggregates
        db.execute(
            text(
                "DELETE FROM revenue_metrics WHERE date_key >= :start AND date_key <= :end"
            ),
            {"start": min_day, "end": max_day},
        )
        for d, (total, count, avg) in sorted(day_totals.items()):
            db.execute(
                text(
                    """
                    INSERT INTO revenue_metrics (date_key, total_revenue, payment_count, average_payment, created_at)
                    VALUES (:date_key, :total, :count, :avg, CURRENT_TIMESTAMP)
                    """
                ),
                {"date_key": d, "total": total, "count": count, "avg": avg},
            )
        db.commit()

    def _load_patient_payment_history(self, db: Session, from_date: datetime | None, to_date: datetime | None) -> None:
        query = (
            db.query(Payment, Invoice)
            .join(Invoice, Payment.invoice_id == Invoice.id)
            .filter(Payment.status == PaymentStatus.SUCCEEDED)
        )
        if from_date:
            query = query.filter(Payment.received_at >= from_date)
        if to_date:
            query = query.filter(Payment.received_at <= to_date)

        rows = query.all()
        if not rows:
            return

        # If we have a range, clear overlapping window first
        if from_date or to_date:
            db.execute(
                text(
                    """
                    DELETE FROM patient_payment_history
                    WHERE (:start IS NULL OR payment_date >= :start)
                      AND (:end IS NULL OR payment_date <= :end)
                    """
                ),
                {
                    "start": from_date.date() if from_date else None,
                    "end": to_date.date() if to_date else None,
                },
            )

        for pay, inv in rows:
            db.execute(
                text(
                    """
                    INSERT INTO patient_payment_history (
                        patient_id, payment_date, amount, payment_status, invoice_id, created_at
                    ) VALUES (:patient_id, :payment_date, :amount, :status, :invoice_id, CURRENT_TIMESTAMP)
                    """
                ),
                {
                    "patient_id": str(inv.patient_id),
                    "payment_date": pay.received_at.date(),
                    "amount": (pay.amount_cents or 0) / 100.0,
                    "status": pay.status.value,
                    "invoice_id": str(pay.invoice_id),
                },
            )
        db.commit()

    def _load_outstanding_payments(self, db: Session) -> None:
        """Rebuild outstanding_payments snapshot from operational tables.

        Definition (initial): invoices where total_amount_cents - sum(succeeded payments) > 0
        days_overdue from invoice.due_date; last_payment_date from max(payment.received_at)
        status: 'overdue' when days_overdue > 0 else 'overdue' (kept simple for MVP)
        """
        # Clear existing snapshot
        db.execute(text("DELETE FROM outstanding_payments"))

        # Aggregate payments per invoice
        payment_rows = db.execute(
            text(
                """
                SELECT invoice_id,
                       COALESCE(SUM(CASE WHEN status = 'SUCCEEDED' THEN amount_cents ELSE 0 END), 0) AS paid_cents,
                       MAX(CASE WHEN status = 'SUCCEEDED' THEN received_at END) AS last_paid_at
                FROM payments
                GROUP BY invoice_id
                """
            )
        ).fetchall()
        paid_by_invoice: Dict[str, Tuple[int, datetime | None]] = {}
        for r in payment_rows:
            paid_by_invoice[str(r[0])] = (int(r[1] or 0), r[2])

        today = datetime.utcnow().date()
        inv_query = db.query(Invoice)
        for inv in inv_query.all():
            paid_cents, last_paid_at = paid_by_invoice.get(str(inv.id), (0, None))
            due_cents = max((inv.total_amount_cents or 0) - paid_cents, 0)
            if due_cents <= 0:
                continue
            days_overdue = 0
            if inv.due_date:
                days_overdue = max((today - inv.due_date).days, 0)
            status = "overdue"
            db.execute(
                text(
                    """
                    INSERT INTO outstanding_payments (
                        patient_id, invoice_id, amount_due, days_overdue, last_payment_date, payment_status, created_at
                    ) VALUES (:patient_id, :invoice_id, :amount_due, :days_overdue, :last_payment_date, :status, CURRENT_TIMESTAMP)
                    """
                ),
                {
                    "patient_id": str(inv.patient_id),
                    "invoice_id": str(inv.id),
                    "amount_due": due_cents / 100.0,
                    "days_overdue": days_overdue,
                    "last_payment_date": last_paid_at.date() if last_paid_at else None,
                    "status": status,
                },
            )
        db.commit()


