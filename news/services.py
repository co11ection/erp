from news.models import Like


class LikeService:
    @staticmethod
    def toggle_like(user, news):
        try:
            like = Like.objects.get(user=user, news=news)
            like.delete()
            return False
        except Like.DoesNotExist:
            Like.objects.create(user=user, news=news)
            return True
