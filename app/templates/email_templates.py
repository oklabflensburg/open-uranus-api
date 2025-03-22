from app.core.config import settings


def reset_password_email_template(reset_token: str) -> dict:
    reset_link = f"{settings.FRONTEND_URL}/reset/password?token={reset_token}"
    subject = "Password Reset Request"
    body = f"""
    Hello,

    You requested to reset your password. Please use the link below to reset it:

    {reset_link}

    If you did not request this, please ignore this email.

    Best regards,
    Your App Team
    """
    return {"subject": subject, "body": body}
