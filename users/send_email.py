from django.core.mail import send_mail
from decouple import config
from celery import shared_task
from config.settings import EMAIL_HOST_USER


@shared_task()
def send_activation_code(email: str, code: str):
    message = f"{config('API_BASE_URL')}/api/account/activate/{code}/"
    html = f"""
    <h1>Для активации нажмите на кнопку</h1>
    <a href="{config('API_BASE_URL')}/api/account/activate/{code}/">
    <button>АКТИВИРОВАТЬ</button>
    </a>
    """

    send_mail(
        subject="Активация аккаунта",
        message=message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=html,
    )
