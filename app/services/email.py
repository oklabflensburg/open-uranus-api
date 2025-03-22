from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
from app.templates.email_templates import reset_password_email_template


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)


async def send_reset_password_email(email: str, reset_token: str):
    template = reset_password_email_template(reset_token)
    message = MessageSchema(
        subject=template["subject"],
        recipients=[email],
        body=template["body"],
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
