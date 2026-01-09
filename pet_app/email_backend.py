"""
Backend de email usando SendGrid (funciona mesmo com portas bloqueadas)
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SendGridEmailBackend:
    """Backend para enviar emails via SendGrid API"""
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    
    def send_messages(self, email_messages):
        """Envia múltiplas mensagens de email"""
        msg_count = 0
        for message in email_messages:
            try:
                self.send_message(message)
                msg_count += 1
            except Exception as e:
                logger.error(f"Erro ao enviar email: {e}")
                if not self.fail_silently:
                    raise
        return msg_count
    
    def send_message(self, message):
        """Envia uma mensagem de email"""
        mail = Mail(
            from_email=message.from_email,
            to_emails=message.to,
            subject=message.subject,
            plain_text_content=message.body,
        )
        
        response = self.sg.send(mail)
        logger.info(f"Email enviado com status: {response.status_code}")
        return response.status_code
