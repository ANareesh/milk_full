"""Email service."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class EmailService:
    """Email service for sending emails."""

    @staticmethod
    def send_password_reset_email(email: str, reset_token: str, user_name: str) -> bool:
        """Send password reset email."""
        try:
            # Create reset link (adjust frontend URL as needed)
            reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
            
            subject = "ASN Dairy Farm - Password Reset Request"
            
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <h2>Password Reset Request</h2>
                <p>Hi {user_name},</p>
                <p>You requested a password reset for your ASN Dairy Farm account.</p>
                <p>Click the link below to reset your password (valid for 30 minutes):</p>
                <p><a href="{reset_link}" style="background-color: #22c55e; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Reset Password</a></p>
                <p>Or copy this link: {reset_link}</p>
                <p>If you didn't request this, please ignore this email.</p>
                <hr>
                <p><small>ASN Dairy Farm Team</small></p>
              </body>
            </html>
            """
            
            return EmailService._send_email(email, subject, html_body)
        except Exception as e:
            logger.error(f"Failed to send reset email to {email}: {str(e)}")
            return False

    @staticmethod
    def _send_email(to_email: str, subject: str, html_body: str) -> bool:
        """Generic method to send email."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.smtp_user
            msg['To'] = to_email
            
            # Attach HTML content
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False