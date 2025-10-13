from typing import Optional
import smtplib
from email.message import EmailMessage
import traceback
import time
import logging
import requests
import os
import ssl
from app.core.config import settings

logger = logging.getLogger(__name__)


class Mailer:
    is_real = False

    def send_email(self, to: str, subject: str, body: str, from_address: Optional[str] = None, html_body: Optional[str] = None) -> None:
        raise NotImplementedError()


class ConsoleMailer(Mailer):
    is_real = False

    def send_email(self, to: str, subject: str, body: str, from_address: Optional[str] = None, html_body: Optional[str] = None) -> None:
        print(f"[MOCK EMAIL] To: {to}\nFrom: {from_address or settings.EMAIL_FROM_ADDRESS}\nSubject: {subject}\n\n{body}")
        if html_body:
            print(f"[MOCK EMAIL HTML]\n{html_body}")


class SMTPMailer(Mailer):
    is_real = True

    def __init__(self, host: str, port: int, username: str, password: str, from_address: Optional[str], retries: int = 3, backoff: float = 0.5):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.retries = retries
        self.backoff = backoff

    def send_email(self, to: str, subject: str, body: str, from_address: Optional[str] = None, html_body: Optional[str] = None) -> None:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_address or self.from_address or settings.EMAIL_FROM_ADDRESS
        msg['To'] = to
        
        if html_body:
            msg.set_content(body)
            msg.add_alternative(html_body, subtype='html')
        else:
            msg.set_content(body)

        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
                    _safe_starttls(smtp)
                    if self.username and self.password:
                        smtp.login(self.username, self.password)
                    smtp.send_message(msg)
                logger.info(f"SMTP mail sent to %s (attempt %d)", to, attempt)
                return
            except Exception as e:
                last_exc = e
                logger.warning("SMTP send attempt %d failed: %s", attempt, e)
                if attempt < self.retries:
                    time.sleep(self.backoff * (2 ** (attempt - 1)))

        # All retries failed
        logger.error("SMTP send failed after %d attempts: %s", self.retries, last_exc)
        raise last_exc


class SendGridMailer(Mailer):
    is_real = True

    def __init__(self, api_key: str, from_address: Optional[str], retries: int = 3, backoff: float = 0.5):
        self.api_key = api_key
        self.from_address = from_address
        self.retries = retries
        self.backoff = backoff

    def send_email(self, to: str, subject: str, body: str, from_address: Optional[str] = None, html_body: Optional[str] = None) -> None:
        url = 'https://api.sendgrid.com/v3/mail/send'
        content = [{'type': 'text/plain', 'value': body}]
        if html_body:
            content.append({'type': 'text/html', 'value': html_body})
        
        payload = {
            'personalizations': [{'to': [{'email': to}]}],
            'from': {'email': from_address or self.from_address or settings.EMAIL_FROM_ADDRESS},
            'subject': subject,
            'content': content
        }
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code in (200, 202):
                    logger.info("SendGrid mail sent to %s (attempt %d)", to, attempt)
                    return
                else:
                    last_exc = Exception(f"SendGrid returned {resp.status_code}: {resp.text}")
                    logger.warning("SendGrid attempt %d failed: %s", attempt, last_exc)
            except Exception as e:
                last_exc = e
                logger.warning("SendGrid send attempt %d exception: %s", attempt, e)

            if attempt < self.retries:
                time.sleep(self.backoff * (2 ** (attempt - 1)))

        logger.error("SendGrid send failed after %d attempts: %s", self.retries, last_exc)
        raise last_exc


def _safe_starttls(smtp):
    """Call starttls while handling missing SSLKEYLOGFILE path issues."""
    try:
        ctx = ssl.create_default_context()
        smtp.starttls(context=ctx)
    except FileNotFoundError as e:
        logging.warning("SSL starttls FileNotFoundError, unsetting SSLKEYLOGFILE and retrying: %s", e)
        os.environ.pop("SSLKEYLOGFILE", None)
        ctx = ssl.create_default_context()
        smtp.starttls(context=ctx)


def get_mailer() -> Mailer:
    # Select provider according to settings.MAIL_PROVIDER or available credentials
    provider = getattr(settings, 'MAIL_PROVIDER', '') or ''
    provider = provider.lower()

    if provider == 'sendgrid' or getattr(settings, 'SENDGRID_API_KEY', ''):
        api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if api_key:
            return SendGridMailer(api_key, settings.EMAIL_FROM_ADDRESS)

    if provider == 'smtp' or (settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD):
        return SMTPMailer(settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.EMAIL_FROM_ADDRESS)

    return ConsoleMailer()
