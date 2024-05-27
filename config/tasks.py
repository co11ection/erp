import requests
from decouple import config
from django.utils import timezone
from .celery import app
from users.send_email import send_activation_code

from news.models import News
from profiles.models import UserProfile

@app.task
def send_email_code_task(to_email, code):
    send_activation_code(to_email, code)


@app.task
def check_and_publish_news():
    current_time = timezone.now()
    news_to_publish = News.objects.filter(
        status=News.STATUS_PENDING, pub_date__lte=current_time
    )
    
    for news in news_to_publish:
        news.status = News.STATUS_PUBLISHED
        news.save()


@app.task
def send_notification_tg(user):
    today = timezone.datetime.weekday()
    if today < 4:
        return
    text = "Отправьте отчеты"
    token = config("TOKEN")
    queryset = UserProfile.objects.all()
    for user in queryset:
        if user.user.telegram_id:
            chat_id = user.user.telegram_id
            url_request = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
            result = requests.get(url=url_request)

# import logging
# from celery import shared_task
# from django.utils import timezone
# from news.models import News

# logger = logging.getLogger(__name__)

# @shared_task
# def check_and_publish_news():
#     try:
#         current_time = timezone.now()
#         news_to_publish = News.objects.filter(
#             status=News.STATUS_PENDING, pub_date__lte=current_time
#         )

#         logger.info(f"Found {news_to_publish.count()} news articles to publish.")

#         for news in news_to_publish:
#             news.status = News.STATUS_PUBLISHED
#             news.save()

#         logger.info("Successfully updated status for all news articles.")

#     except Exception as e:
#         logger.error(f"An error occurred: {str(e)}")