import base64
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from .models import User
from django.core.exceptions import ObjectDoesNotExist


def change_photo(user_profile, photo: str):
    user = user_profile.user
    if photo:
        format, imgstr = photo.split(";base64,")
        ext = format.split("/")[-1]
        data = ContentFile(
            base64.b64decode(imgstr), name=f"{user_profile.user.first_name}_ava.{ext}"
        )
        user.photo = data

    else:
        user.photo = None

    user.save()


def get_user_by_email(email):
    try:
        user = User.objects.get(email__iexact=email)
        return user
    except User.DoesNotExist:
        return None
