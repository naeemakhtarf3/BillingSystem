from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import stripe
import uuid
from datetime import datetime
from app.db.session import get_db
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentStatus
from app.models.staff import Staff
from app.schemas.payment import PaymentResponse, PaymentCreate
from app.schemas.payment import PaymentListItem
from app.models.patient import Patient
from app.api.api_v1.endpoints.auth import get_current_staff
from app.core.config import settings
from app.services.audit_service import create_audit_log
from app.services.mailer import get_mailer
import logging

router = APIRouter()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Ensure stripe api key from settings is applied at runtime if present
if not getattr(stripe, "api_key", None):
    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)

# Ensure Stripe module is properly loaded
def _ensure_stripe_loaded():
    """Ensure Stripe module is properly loaded and configured"""
    import stripe
    if not stripe.api_key:
        stripe.api_key = settings.STRIPE_SECRET_KEY
    if not stripe.checkout:
        import stripe.checkout
    return stripe.checkout and hasattr(stripe.checkout, 'Session')


def _create_checkout_session(invoice, request: Request = None):
    """Create a Stripe Checkout Session or return a fake session when Stripe isn't configured.
    If request is provided we prefer building a backend absolute URL for local checkout pages.
    """
    # ensure runtime stripe key from settings if available
    if not getattr(stripe, "api_key", None) and getattr(settings, "STRIPE_SECRET_KEY", None):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    # Real Stripe (when SDK and API key available)
    if _ensure_stripe_loaded() and stripe.api_key:
        return stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': (invoice.currency or "USD").lower(),
                    'product_data': {
                        'name': f'Invoice {invoice.invoice_number}',
                        'description': f'Payment for invoice {invoice.invoice_number}',
                    },
                    'unit_amount': int(invoice.total_amount_cents or 0),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{settings.CORS_ORIGINS[0]}/patient/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.CORS_ORIGINS[0]}/patient/payment/cancelled',
            metadata={
                'invoice_id': str(invoice.id),
                'clinic_id': getattr(settings, "CLINIC_ID", "clinic_001")
            }
        )

    # Fallback fake session (local dev/test)
    class _FakeSession:
        def __init__(self, id, url):
            self.id = id
            self.url = url

    fake_id = f"local_cs_{uuid.uuid4().hex}"

    # Build backend-local URL using request.url_for when available, else use configured origin
    if request is not None:
        try:
            fake_url = str(request.url_for("local_checkout_page", session_id=fake_id))
        except Exception:
            base = settings.CORS_ORIGINS[0].rstrip('/')
            fake_url = f"{base}/api/v1/payments/local-checkout/{fake_id}"
    else:
        base = settings.CORS_ORIGINS[0].rstrip('/')
        fake_url = f"{base}/api/v1/payments/local-checkout/{fake_id}"

    return _FakeSession(fake_id, fake_url)


@router.post("/invoices/{invoice_id}/create-payment-link")
def create_payment_link(
    invoice_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    # Ensure invoice_id is a UUID for DB lookup
    try:
        invoice_uuid = uuid.UUID(str(invoice_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice.status not in [InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice must be issued or partially paid to create payment link"
        )
    
    try:
        # Create Stripe Checkout Session (or fake one in test/dev env)
        checkout_session = _create_checkout_session(invoice, request)

        invoice.stripe_checkout_session_id = checkout_session.id
        db.commit()

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe/create session error: {str(e)}"
        )


@router.post("/invoices/{invoice_id}/create-payment-link-public")
def create_payment_link_public(
    invoice_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Public endpoint for patients to create payment links without authentication"""
    # Ensure invoice_id is a UUID for DB lookup
    try:
        invoice_uuid = uuid.UUID(str(invoice_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice.status not in [InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice must be issued or partially paid to create payment link"
        )
    
    try:
        # Create Stripe Checkout Session (or fake one in test/dev env)
        checkout_session = _create_checkout_session(invoice, request)

        invoice.stripe_checkout_session_id = checkout_session.id
        db.commit()

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe/create session error: {str(e)}"
        )


@router.post("/invoices/{invoice_id}/send-payment-link")
def send_payment_link(
    invoice_id: str,
    request: Request,
    email: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Issue invoice if needed, create a Stripe payment link and (mock) send it to the provided email.
    For now if email is not provided we'll use a hardcoded address per requirements.
    """
    try:
        invoice_uuid = uuid.UUID(str(invoice_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    # Issue invoice if it's still draft
    if invoice.status == InvoiceStatus.DRAFT:
        invoice.status = InvoiceStatus.ISSUED
        invoice.issued_at = datetime.utcnow()
        db.commit()
        db.refresh(invoice)

    try:
        checkout_session = _create_checkout_session(invoice, request)

        # persist the checkout session id
        invoice.stripe_checkout_session_id = checkout_session.id
        db.commit()

        # Send email via configured mailer (console by default in dev/test)
        send_to = email or 'naeem.akhtar@f3technologies.eu'
        mailer = get_mailer()

        send_fn = getattr(mailer, "send_email", None)
        if send_fn is None:
            raise RuntimeError("Mailer has no send_email method")

        try:
            # Create HTML email content
            amount_display = f"{(invoice.total_amount_cents or 0) / 100:.2f}"
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Payment Request - Invoice {invoice.invoice_number}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                    }}
                    .invoice-details {{
                        background-color: #ffffff;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 20px;
                    }}
                    .payment-button {{
                        display: inline-block;
                        background-color: #007bff;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 16px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .payment-button:hover {{
                        background-color: #0056b3;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        font-size: 14px;
                        color: #6c757d;
                    }}
                    .amount {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #28a745;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Payment Request</h1>
                    <p>You have an outstanding invoice that requires payment.</p>
                </div>
                
                <div class="invoice-details">
                    <h2>Invoice Details</h2>
                    <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
                    <p><strong>Amount Due:</strong> <span class="amount">${amount_display} {invoice.currency}</span></p>
                    <p><strong>Due Date:</strong> {invoice.due_date.strftime('%B %d, %Y') if invoice.due_date else 'Not specified'}</p>
                </div>
                
                <div style="text-align: center;">
                    <a href="{checkout_session.url}" class="payment-button" target="_blank">
                        Complete Payment
                    </a>
                </div>
                
                <p>Click the button above to securely complete your payment. You will be redirected to our secure payment processor.</p>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                    {checkout_session.url}
                </p>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>If you have any questions about this invoice, please contact our billing department.</p>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for email clients that don't support HTML
            plain_body = f"""
Payment Request - Invoice {invoice.invoice_number}

You have an outstanding invoice that requires payment.

Invoice Details:
- Invoice Number: {invoice.invoice_number}
- Amount Due: ${amount_display} {invoice.currency}
- Due Date: {invoice.due_date.strftime('%B %d, %Y') if invoice.due_date else 'Not specified'}

To complete your payment, please visit:
{checkout_session.url}

This is an automated message. Please do not reply to this email.
If you have any questions about this invoice, please contact our billing department.
            """
            
            # Send email using the configured mailer
            send_fn(
                to=send_to,
                subject=f'Payment Request - Invoice {invoice.invoice_number}',
                body=plain_body,
                html_body=html_body,
                from_address=settings.EMAIL_FROM_ADDRESS
            )
            

            # persist a record that we sent the email and commit
            if hasattr(invoice, "email_sent_to"):
                invoice.email_sent_to = send_to
            if hasattr(invoice, "email_sent_at"):
                invoice.email_sent_at = datetime.utcnow()
            # optional debug field if present
            if hasattr(invoice, "ERROR"):
                invoice.ERROR = f"Sent email to {send_to}"
            db.commit()

        except Exception as e:
            logging.exception("[MAILER ERROR] Could not send email")
            if hasattr(invoice, "ERROR"):
                invoice.ERROR = f"[MAILER ERROR] Could not send email to {send_to}: {e}"
            try:
                db.commit()
            except Exception:
                logging.exception("Failed to commit invoice error state")

            return {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "sent_to": send_to,
                "mail_error": str(e)
            }

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "sent_to": send_to
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email: {e}")

@router.get("/invoices/{invoice_id}/payments", response_model=List[PaymentResponse])
def get_invoice_payments(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    try:
        invoice_uuid = uuid.UUID(str(invoice_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    payments = db.query(Payment).filter(Payment.invoice_id == invoice_uuid).all()
    return payments


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    # Only billing staff and admin can create manual payments
    if current_staff.role not in ["admin", "billing_clerk"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to create payments")

    # Accept either a UUID invoice id or an invoice_number (e.g. CLINIC-2025...)
    invoice_uuid = None
    if payload.invoice_id:
        try:
            invoice_uuid = uuid.UUID(str(payload.invoice_id))
        except Exception:
            # Not a UUID, try to resolve by invoice_number
            invoice_obj = db.query(Invoice).filter(Invoice.invoice_number == str(payload.invoice_id)).first()
            if invoice_obj:
                invoice_uuid = invoice_obj.id
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id or invoice number")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    if invoice.status == InvoiceStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add payment to cancelled invoice")

    # Create a manual payment record
    payment = Payment(
        invoice_id=invoice_uuid,
        # For manual/cash payments we set a generated manual id so DB NOT NULL/unique constraint is satisfied
        stripe_payment_id=f"manual_{uuid.uuid4().hex}",
        amount_cents=payload.amount_cents,
        currency=payload.currency.upper(),
        status=PaymentStatus.SUCCEEDED,
        raw_event={"method": payload.method, "note": payload.note}
    )
    if payload.received_at:
        payment.received_at = payload.received_at

    db.add(payment)

    # Compute total paid and update invoice status
    db.flush()
    total_paid = db.query(func.coalesce(func.sum(Payment.amount_cents), 0)).filter(
        Payment.invoice_id == invoice_uuid,
        Payment.status == PaymentStatus.SUCCEEDED
    ).scalar() or 0

    if total_paid >= invoice.total_amount_cents:
        invoice.status = InvoiceStatus.PAID
    elif total_paid > 0:
        invoice.status = InvoiceStatus.PARTIALLY_PAID

    db.commit()
    db.refresh(payment)

    # Build JSON-serializable response (convert UUIDs to strings)
    response = {
        "id": str(payment.id),
        "invoice_id": str(payment.invoice_id) if payment.invoice_id else None,
        "invoice_number": invoice.invoice_number,
        "stripe_payment_id": payment.stripe_payment_id,
        "amount_cents": payment.amount_cents,
        "currency": payment.currency,
        "status": payment.status,
        "received_at": payment.received_at,
        "raw_event": payment.raw_event
    }

    # Audit log for manual payment creation
    try:
        create_audit_log(
            db,
            actor_id=getattr(current_staff, 'id', None),
            actor_type='staff',
            action='create_payment',
            target_type='payment',
            target_id=str(payment.id),
            details={
                'invoice_id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'amount_cents': payment.amount_cents,
                'method': payload.method
            }
        )
    except Exception as e:
        # don't block main flow if audit logging fails; print for debugging
        import traceback
        print('[AUDIT ERROR] failed to create audit log for payment:', e)
        traceback.print_exc()

    return response


@router.get("/", response_model=List[PaymentListItem])
def list_payments(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    # Build base query joining invoices and patients
    query = db.query(Payment, Invoice, Patient).join(Invoice, Payment.invoice_id == Invoice.id).join(Patient, Invoice.patient_id == Patient.id)

    if status:
        try:
            stat_enum = PaymentStatus(status)
            query = query.filter(Payment.status == stat_enum)
        except Exception:
            pass

    results = query.order_by(Payment.received_at.desc()).offset(skip).limit(limit).all()

    items = []
    for payment, invoice, patient in results:
        items.append({
            'id': str(payment.id),
            'invoice_id': str(payment.invoice_id),
            'invoice_number': invoice.invoice_number,
            'patient_id': str(patient.id),
            'patient_name': patient.name,
            'patient_email': patient.email,
            'stripe_payment_id': payment.stripe_payment_id,
            'amount_cents': payment.amount_cents,
            'currency': payment.currency,
            'status': payment.status,
            'received_at': payment.received_at
        })

    return items

@router.post("/{payment_id}/refund")
def refund_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    # Only admin can process refunds
    if current_staff.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for refund"
        )
    
    try:
        payment_uuid = uuid.UUID(str(payment_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment id")

    payment = db.query(Payment).filter(Payment.id == payment_uuid).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only succeeded payments can be refunded"
        )
    
    try:
        # Process refund through Stripe
        refund = stripe.Refund.create(
            payment_intent=payment.stripe_payment_id,
            reason='requested_by_customer'
        )
        
        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        db.commit()
        # Audit log for refund
        try:
            create_audit_log(
                db,
                actor_id=getattr(current_staff, 'id', None),
                actor_type='staff',
                action='refund_payment',
                target_type='payment',
                target_id=str(payment.id),
                details={'refund_id': refund.id, 'amount': refund.amount}
            )
        except Exception as e:
            import traceback
            print('[AUDIT ERROR] failed to create audit log for refund:', e)
            traceback.print_exc()

        return {
            "refund_id": refund.id,
            "status": "refunded",
            "amount": refund.amount
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe refund error: {str(e)}"
        )

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks for payment events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        invoice_id = session.get('metadata', {}).get('invoice_id')

        if invoice_id:
            # convert invoice_id to UUID for DB queries
            try:
                invoice_uuid = uuid.UUID(str(invoice_id))
            except Exception:
                invoice_uuid = None

            # Check if payment already exists (idempotency)
            existing_payment = db.query(Payment).filter(
                Payment.stripe_payment_id == session.get('payment_intent')
            ).first()

            if not existing_payment:
                # Verify invoice exists and that the session id matches the stored checkout session
                invoice = None
                if invoice_uuid:
                    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()

                # If invoice exists and a checkout session id was stored, ensure it matches the incoming session id
                incoming_session_id = session.get('id')
                if invoice and invoice.stripe_checkout_session_id and incoming_session_id and invoice.stripe_checkout_session_id != incoming_session_id:
                    # Mismatch: ignore this webhook to avoid marking the wrong invoice paid
                    print(f"[WEBHOOK] Ignoring checkout.session.completed for session {incoming_session_id} because it does not match invoice {invoice.invoice_number} stored session {invoice.stripe_checkout_session_id}")
                else:
                    # Create payment record
                    payment = Payment(
                        invoice_id=invoice_uuid or None,
                        stripe_payment_id=session.get('payment_intent'),
                        amount_cents=session.get('amount_total'),
                        currency=session.get('currency', '').upper(),
                        status=PaymentStatus.SUCCEEDED,
                        raw_event=event
                    )
                    db.add(payment)

                    # Update invoice status when possible
                    if invoice:
                        invoice.status = InvoiceStatus.PAID

                    db.commit()

                    # Create an audit entry for the automatic Stripe payment
                    try:
                        create_audit_log(
                            db,
                            actor_id=None,
                            actor_type='stripe',
                            action='checkout_completed',
                            target_type='payment',
                            target_id=str(payment.id),
                            details={
                                'invoice_id': str(invoice.id) if invoice else None,
                                'session_id': incoming_session_id,
                                'payment_intent': session.get('payment_intent')
                            }
                        )
                    except Exception as e:
                        print('[AUDIT ERROR] failed to create audit log for stripe webhook payment:', e)
                        import traceback
                        traceback.print_exc()
    
    return {"status": "success"}

@router.get("/local-checkout/{session_id}", response_class=HTMLResponse)
def local_checkout_page(session_id: str, db: Session = Depends(get_db)):
    """
    Simple local checkout page for environments without Stripe.
    Looks up the invoice by stripe_checkout_session_id and presents a 'Pay' button.
    The form now POSTs to /local-checkout/{session_id}/start which will:
      - create a real Stripe Checkout session and redirect to Stripe when keys are configured, or
      - fall back to the local simulated completion which creates the Payment and marks invoice paid.
    """
    invoice = db.query(Invoice).filter(Invoice.stripe_checkout_session_id == session_id).first()
    if not invoice:
        html = f"""
        <html><body>
        <h1>Checkout Session Not Found</h1>
        <p>No invoice associated with session id: {session_id}</p>
        </body></html>
        """
        return HTMLResponse(content=html, status_code=404)

    amount_display = f"{(invoice.total_amount_cents or 0) / 100:.2f}"
    html = f"""
    <html>
      <head><title>Pay Invoice {invoice.invoice_number}</title></head>
      <body>
        <h1>Pay Invoice {invoice.invoice_number}</h1>
        <p>Amount: {amount_display} {invoice.currency}</p>
        <!-- POSTs to /start which will try to create a real Stripe Checkout session -->
        <form method="post" action="/api/v1/payments/local-checkout/{session_id}/start">
          <button type="submit">Complete Payment</button>
        </form>
        <p>This is a local/dev checkout. If Stripe is configured you'll be redirected to Stripe Checkout.
           If not, the backend will simulate the payment and mark the invoice paid.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/local-checkout/{session_id}/start")
def local_checkout_start(session_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Start a Stripe Checkout flow for the local session id when Stripe is configured.
    Falls back to the local completion behavior if Stripe is not configured or session creation fails.
    """
    invoice = db.query(Invoice).filter(Invoice.stripe_checkout_session_id == session_id).first()
    if not invoice:
        cancel_url = f"{settings.CORS_ORIGINS[0]}/patient/payment/cancelled"
        return RedirectResponse(url=cancel_url, status_code=303)

    # Helper to perform local simulated completion (create Payment, mark invoice paid, audit) and redirect
    def _simulate_and_redirect():
        try:
            payment = Payment(
                invoice_id=invoice.id,
                stripe_payment_id=f"local_payment_{uuid.uuid4().hex}",
                amount_cents=invoice.total_amount_cents,
                currency=(invoice.currency or "USD").upper(),
                status=PaymentStatus.SUCCEEDED,
                raw_event={"local_checkout": True, "session_id": session_id, "invoice_id": str(invoice.id)}
            )
            db.add(payment)
            invoice.status = InvoiceStatus.PAID
            db.commit()
            db.refresh(payment)

            try:
                create_audit_log(
                    db,
                    actor_id=None,
                    actor_type='local_checkout',
                    action='checkout_completed',
                    target_type='payment',
                    target_id=str(payment.id),
                    details={
                        'invoice_id': str(invoice.id),
                        'session_id': session_id,
                        'payment_id': payment.stripe_payment_id,
                        'amount_cents': payment.amount_cents
                    }
                )
            except Exception:
                logging.exception("[AUDIT ERROR] failed to create audit log for local checkout payment")

        except Exception:
            logging.exception("Failed to simulate local checkout")
            cancel_url = f"{settings.CORS_ORIGINS[0]}/patient/payment/cancelled"
            return RedirectResponse(url=cancel_url, status_code=303)

        success_url = f"{settings.CORS_ORIGINS[0]}/patient/payment/success?session_id={session_id}"
        return RedirectResponse(url=success_url, status_code=303)

    # Verify Stripe is configured (API key present) and SDK exposes checkout.Session
    if not (getattr(stripe, "api_key", None) and stripe.api_key):
        # Stripe not configured -> simulate
        logging.info("Stripe not configured, falling back to local simulation for session %s", session_id)
        return _simulate_and_redirect()

    # Try to create a real Stripe Checkout Session and redirect the browser to it
    try:
        # Ensure Stripe is properly initialized
        if not _ensure_stripe_loaded():
            raise Exception("Stripe checkout module not properly loaded")
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': (invoice.currency or "USD").lower(),
                    'product_data': {
                        'name': f'Invoice {invoice.invoice_number}',
                        'description': f'Payment for invoice {invoice.invoice_number}',
                    },
                    'unit_amount': int(invoice.total_amount_cents or 0),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{settings.CORS_ORIGINS[0]}/patient/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.CORS_ORIGINS[0]}/patient/payment/cancelled',
            metadata={
                'invoice_id': str(invoice.id),
                'local_session_id': session_id
            }
        )

        # Persist Stripe session id so webhook can verify
        invoice.stripe_checkout_session_id = checkout_session.id
        db.commit()

        # Redirect browser to Stripe-hosted checkout page
        return RedirectResponse(url=checkout_session.url, status_code=303)

    except Exception as e:
        logging.exception("Failed to create Stripe Checkout session for local session %s: %s", session_id, e)
        # Fall back to local simulation
        return _simulate_and_redirect()


@router.post("/verify-payment-success")
def verify_payment_success(
    session_id: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Verify Stripe payment session and process payment if successful.
    This endpoint is called from the frontend payment success page.
    """
    try:
        # Retrieve the Stripe session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if payment was successful
        if session.payment_status != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment was not successful"
            )
        
        # Get invoice ID from session metadata
        invoice_id = session.metadata.get('invoice_id')
        if not invoice_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No invoice ID found in session metadata"
            )
        
        # Convert to UUID
        try:
            invoice_uuid = uuid.UUID(str(invoice_id))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid invoice ID format"
            )
        
        # Find the invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Check if payment already exists (idempotency)
        existing_payment = db.query(Payment).filter(
            Payment.stripe_payment_id == session.payment_intent
        ).first()
        
        if existing_payment:
            # Payment already processed, return success
            return {
                "status": "success",
                "message": "Payment already processed",
                "invoice_number": invoice.invoice_number,
                "amount_paid": existing_payment.amount_cents / 100
            }
        
        # Create payment record
        payment = Payment(
            invoice_id=invoice_uuid,
            stripe_payment_id=session.payment_intent,
            amount_cents=session.amount_total,
            currency=session.currency.upper(),
            status=PaymentStatus.SUCCEEDED,
            raw_event=session
        )
        db.add(payment)
        
        # Update invoice status to paid
        invoice.status = InvoiceStatus.PAID
        db.commit()
        db.refresh(payment)
        
        # Create audit log
        try:
            create_audit_log(
                db,
                actor_id=None,
                actor_type='stripe',
                action='payment_verified',
                target_type='payment',
                target_id=str(payment.id),
                details={
                    'invoice_id': str(invoice.id),
                    'invoice_number': invoice.invoice_number,
                    'session_id': session_id,
                    'payment_intent': session.payment_intent,
                    'amount_cents': payment.amount_cents
                }
            )
        except Exception as e:
            logging.exception("[AUDIT ERROR] failed to create audit log for payment verification: %s", e)
        
        return {
            "status": "success",
            "message": "Payment processed successfully",
            "invoice_number": invoice.invoice_number,
            "amount_paid": payment.amount_cents / 100,
            "currency": payment.currency
        }
        
    except stripe.error.StripeError as e:
        logging.exception("Stripe error during payment verification: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logging.exception("Error during payment verification: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during payment verification"
        )