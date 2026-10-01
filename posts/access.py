from follows.models import Block, Follow
from .models import Post


def can_view_post(user, post):
    """Visibility rules shared by feed, post details, actions, and comments."""
    if not user or not user.is_authenticated:
        return False

    if post.status != Post.Status.ACTIVE:
        return False

    if post.author_id == user.id:
        return True

    # A block in either direction prevents interaction and viewing.
    if Block.objects.filter(blocker_id=user.id, blocked_id=post.author_id).exists():
        return False
    if Block.objects.filter(blocker_id=post.author_id, blocked_id=user.id).exists():
        return False

    if post.visibility == Post.Visibility.PUBLIC:
        return True

    if post.visibility == Post.Visibility.FOLLOWERS:
        return Follow.objects.filter(
            follower_id=user.id, following_id=post.author_id
        ).exists()

    # There is no Group/GroupMembership model in the supplied codebase.
    # Until that module exists, GROUP posts are visible only to their author.
    return False
