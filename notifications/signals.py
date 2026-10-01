from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import create_notification

@receiver(post_save, sender="follows.Follow")
def notify_follow(sender, instance, created, **kwargs):
    if created:
        create_notification(instance.following, "FOLLOW", "New follower",
                            "Someone started following you.", actor=instance.follower,
                            target_type="profile", target_id=instance.follower_id)

@receiver(post_save, sender="posts.PostLike")
def notify_like(sender, instance, created, **kwargs):
    if created:
        create_notification(instance.post.author, "LIKE", "Your post was liked",
                            "Someone liked your post.", actor=instance.user,
                            target_type="post", target_id=instance.post_id)

@receiver(post_save, sender="comments.Comment")
def notify_comment(sender, instance, created, **kwargs):
    if created:
        create_notification(instance.post.author, "COMMENT", "New comment on your post",
                            instance.content[:500], actor=instance.author,
                            target_type="post", target_id=instance.post_id)
