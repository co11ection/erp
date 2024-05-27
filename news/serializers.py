from rest_framework import serializers
from .models import News
from profiles.serializers import UserProfileSerializer


class NewsSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    user_liked_photo = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "text",
            "image",
            "pub_date",
            "status",
            "total_likes",
            "user_liked",
            "user_liked_photo",
        ]

    def get_total_likes(self, obj):
        return obj.total_likes.count()

    def get_user_liked(self, obj):
        return list(obj.total_likes.values_list("first_name", flat=True))
    
    def get_user_liked_photo(self, obj):
        return list(obj.total_likes.values_list("photo", flat=True))


class PublishedNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "text", "image", "pub_date", "likes"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.status != "Опубликовано":
            data["text"] = "Эта новость " "не опубликована и не доступна для просмотра."
        return data
