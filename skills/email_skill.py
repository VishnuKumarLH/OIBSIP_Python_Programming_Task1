import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS

logger = logging.getLogger(__name__)

class EmailSkill:


    def __init__(self):
       
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_pass = SMTP_PASS

    def send_email(self, recipient, subject, body):
       
        if not all([recipient, subject, body]):
            return False, "Missing required email parameters (recipient, subject, or body)"

        if not self._validate_email(recipient):
            return False, f"Invalid email address: {recipient}"

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Secure the connection
            server.login(self.smtp_user, self.smtp_pass)

            # Send email
            text = msg.as_string()
            server.sendmail(self.smtp_user, recipient, text)
            server.quit()

            logger.info(f"Email sent successfully to {recipient}")
            return True, f"Email sent successfully to {recipient}"

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check your email credentials.")
            return False, "Authentication failed. Please check your email credentials in the .env file."

        except smtplib.SMTPConnectError:
            logger.error(f"Failed to connect to SMTP server {self.smtp_host}:{self.smtp_port}")
            return False, f"Failed to connect to email server. Please check your SMTP settings."

        except smtplib.SMTPRecipientsRefused:
            logger.error(f"Email recipient {recipient} was refused by the server")
            return False, f"Email address {recipient} was rejected by the server."

        except smtplib.SMTPServerDisconnected:
            logger.error("SMTP server disconnected unexpectedly")
            return False, "Email server disconnected. Please try again."

        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False, f"An unexpected error occurred while sending email: {str(e)}"

    def _validate_email(self, email):
       
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def test_connection(self):
       
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.quit()
            return True, "SMTP connection test successful"
        except Exception as e:
            return False, f"SMTP connection test failed: {str(e)}"
