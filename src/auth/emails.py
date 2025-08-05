from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from starlette.templating import Jinja2Templates

from core.config import settings

TEMPLATE_DIR = settings.BASE_DIR / "templates"


async def send_verification_email1(to_email: str, token: str) -> None:
    confirmation_url = f"{settings.FRONTEND_URL}/auth/verify?token=${token}"
    templates = Jinja2Templates(directory=TEMPLATE_DIR)
    template = templates.get_template(name="confirmation_email.html")
    html_content = template.render(confirmation_url=confirmation_url)

    message = MIMEMultipart("alternative")
    message["From"] = settings.MAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"
    html_message = MIMEText(html_content, "html", "utf-8")
    message.attach(html_message)

    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        use_tls=True,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        timeout=5.0,
    )


async def send_email(
    to_email: str, subject: str, template_name: str, context: dict
) -> None:
    templates = Jinja2Templates(directory=TEMPLATE_DIR)
    template = templates.get_template(name=template_name)
    html_content = template.render(**context)

    message = MIMEMultipart("alternative")
    message["From"] = settings.MAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    html_message = MIMEText(html_content, "html", "utf-8")
    message.attach(html_message)

    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        use_tls=True,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        timeout=5.0,
    )


async def send_verification_email(to_email: str, token: str) -> None:
    confirmation_url = f"{settings.FRONTEND_URL}/auth/verify?token=${token}"
    context = {"confirmation_url": confirmation_url}
    await send_email(
        to_email,
        "Подтверждение регистрации",
        "confirmation_email.html",
        context,
    )


async def send_confirmation_reset_password(to_email: str, token: str) -> None:
    context = {"token": token}
    await send_email(to_email, "Сброс пароля", "reset_password.html", context)
