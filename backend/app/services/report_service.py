from __future__ import annotations

from typing import Any, Dict, List, Tuple
from datetime import date
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas
from io import BytesIO


class ReportService:
    """Service providing report query interfaces and PDF export scaffolding."""

    def get_revenue_report(self, db: Session, **filters: Any) -> Dict[str, Any]:
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        granularity = (filters.get("granularity") or "month").lower()

        rows = db.execute(
            text(
                """
                SELECT date_key, total_revenue, payment_count, average_payment
                FROM revenue_metrics
                WHERE (:start IS NULL OR date_key >= :start)
                  AND (:end IS NULL OR date_key <= :end)
                ORDER BY date_key ASC
                """
            ),
            {"start": start_date, "end": end_date},
        ).fetchall()

        def month_key(d: date) -> date:
            return date(d.year, d.month, 1)

        def week_key(d: date) -> date:
            # ISO week start (Monday)
            return d - timedelta(days=d.weekday())

        if granularity == "day":
            points = [
                {
                    "date": (r[0] if isinstance(r[0], date) else date.fromisoformat(str(r[0]))).isoformat(),
                    "totalRevenue": float(r[1] or 0),
                    "paymentCount": int(r[2] or 0),
                    "averagePayment": float(r[3] or 0),
                }
                for r in rows
            ]
        else:
            from datetime import timedelta

            buckets: Dict[date, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
            for r in rows:
                d = r[0] if isinstance(r[0], date) else date.fromisoformat(str(r[0]))
                key = month_key(d) if granularity == "month" else week_key(d)
                total, count = buckets[key]
                total += float(r[1] or 0)
                count += int(r[2] or 0)
                buckets[key] = (total, count)
            points: List[Dict[str, Any]] = []
            for k in sorted(buckets.keys()):
                total, count = buckets[k]
                avg = (total / count) if count else 0.0
                points.append(
                    {
                        "date": k.isoformat(),
                        "totalRevenue": float(total),
                        "paymentCount": int(count),
                        "averagePayment": float(avg),
                    }
                )

        return {"granularity": granularity, "points": points}

    def generate_revenue_pdf(self, db: Session, **filters: Any) -> bytes:
        data = self.get_revenue_report(db, **filters)
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.setTitle("Revenue Report")
        c.drawString(50, 800, "Revenue Report")
        c.drawString(50, 780, f"Granularity: {data.get('granularity')}")
        y = 750
        for p in data.get("points", [])[:40]:
            c.drawString(50, y, f"{p['date']}  Total: ${p['totalRevenue']:.2f}  Count: {p['paymentCount']}  Avg: ${p['averagePayment']:.2f}")
            y -= 18
            if y < 60:
                c.showPage()
                y = 800
        c.showPage()
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def generate_outstanding_csv(self, db: Session, **filters: Any) -> str:
        """Generate CSV format for outstanding payments report"""
        data = self.get_outstanding_payments(db=db, **filters)
        
        # CSV headers
        headers = ["PatientID", "InvoiceID", "AmountDue", "DaysOverdue", "LastPayment", "Status"]
        
        # Create CSV content
        csv_lines = [",".join(headers)]
        
        for item in data.get("items", []):
            row = [
                str(item['patientId']),
                str(item['invoiceId']),
                f"{item['amountDue']:.2f}",
                str(item['daysOverdue']),
                str(item['lastPaymentDate'] or ''),
                str(item['status'])
            ]
            csv_lines.append(",".join(row))
        
        return "\n".join(csv_lines)

    def get_patient_history(self, db: Session, patient_id: str, **filters: Any) -> Dict[str, Any]:
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        status = filters.get("status")

        rows = db.execute(
            text(
                """
                SELECT payment_date, amount, payment_status, invoice_id
                FROM patient_payment_history
                WHERE patient_id = :pid
                  AND (:start IS NULL OR payment_date >= :start::date)
                  AND (:end IS NULL OR payment_date <= :end::date)
                  AND (:status IS NULL OR payment_status = :status)
                ORDER BY payment_date ASC
                """
            ),
            {"pid": patient_id, "start": start_date, "end": end_date, "status": status},
        ).fetchall()

        return {
            "patientId": patient_id,
            "payments": [
                {
                    "paymentDate": r[0].isoformat(),
                    "amount": float(r[1] or 0),
                    "status": r[2],
                    "invoiceId": r[3],
                }
                for r in rows
            ],
        }

    def get_outstanding_payments(self, **filters: Any) -> Dict[str, Any]:
        db: Session = filters.get("db")
        min_days_overdue = filters.get("min_days_overdue")
        max_days_overdue = filters.get("max_days_overdue")
        min_amount = filters.get("min_amount")
        max_amount = filters.get("max_amount")

        where = ["1=1"]
        params: Dict[str, Any] = {}
        if min_days_overdue is not None:
            where.append("days_overdue >= :min_days")
            params["min_days"] = min_days_overdue
        if max_days_overdue is not None:
            where.append("days_overdue <= :max_days")
            params["max_days"] = max_days_overdue
        if min_amount is not None:
            where.append("amount_due >= :min_amt")
            params["min_amt"] = min_amount
        if max_amount is not None:
            where.append("amount_due <= :max_amt")
            params["max_amt"] = max_amount

        rows = db.execute(
            text(
                f"""
                SELECT patient_id, invoice_id, amount_due, days_overdue, last_payment_date, payment_status
                FROM outstanding_payments
                WHERE {' AND '.join(where)}
                ORDER BY days_overdue DESC, amount_due DESC
                """
            ),
            params,
        ).fetchall()

        items = [
            {
                "patientId": r[0],
                "invoiceId": r[1],
                "amountDue": float(r[2] or 0),
                "daysOverdue": int(r[3] or 0),
                "lastPaymentDate": r[4].isoformat() if r[4] else None,
                "status": r[5],
            }
            for r in rows
        ]
        return {"items": items, "total": len(items)}


