from rest_framework import serializers
from .models import Post, PostMedia, PostLike, SavedPost


class PostMediaSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = ["id", "url", "created_at"]
        read_only_fields = fields

    def get_url(self, obj):
        try:
            return obj.image.url
        except (ValueError, AttributeError):
            return None


class PostSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True,
        max_length=4,
    )
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    shares_count = serializers.SerializerMethodField()
    saves_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    caption = serializers.CharField(max_length=500, allow_blank=False, trim_whitespace=True)

    class Meta:
        model = Post
        fields = [
            "id", "author_id", "caption", "visibility", "activity_id", "place_id",
            "status", "media", "photos", "likes_count", "comments_count",
            "shares_count", "saves_count", "is_liked", "is_saved",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "author_id", "status", "media", "likes_count", "comments_count",
            "shares_count", "saves_count", "is_liked", "is_saved",
            "created_at", "updated_at",
        ]

    def validate_caption(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Caption is required.")
        if len(value) > 500:
            raise serializers.ValidationError("Caption must be 500 characters or fewer.")
        return value

    def validate(self, attrs):
        visibility = attrs.get("visibility", getattr(self.instance, "visibility", Post.Visibility.PUBLIC))
        if visibility not in Post.Visibility.values:
            raise serializers.ValidationError({"visibility": "Invalid visibility value."})
        photos = attrs.get("photos", [])
        if len(photos) > 4:
            raise serializers.ValidationError({"photos": "You can upload up to 4 photos."})
        return attrs

    def _replace_photos(self, post, photos):
        # PATCH with photos replaces the existing photo set.
        for old in post.media.all():
            if old.image:
                old.image.delete(save=False)
            old.delete()
        for photo in photos:
            PostMedia.objects.create(post=post, image=photo)

    def create(self, validated_data):
        photos = validated_data.pop("photos", [])
        post = Post.objects.create(**validated_data)
        for photo in photos:
            PostMedia.objects.create(post=post, image=photo)
        return post

    def update(self, instance, validated_data):
        photos = validated_data.pop("photos", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if photos is not None:
            self._replace_photos(instance, photos)
        return instance

    def get_likes_count(self, obj):
        return getattr(obj, "likes_count_value", obj.likes.count())

    def get_comments_count(self, obj):
        return getattr(obj, "comments_count_value", obj.comments.count())

    def get_shares_count(self, obj):
        return getattr(obj, "shares_count_value", obj.shares.count())

    def get_saves_count(self, obj):
        return getattr(obj, "saves_count_value", obj.saves.count())

    def get_is_liked(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and PostLike.objects.filter(post=obj, user=request.user).exists())

    def get_is_saved(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and SavedPost.objects.filter(post=obj, user=request.user).exists())


class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = SavedPost
        fields = ["id", "post", "created_at"]
        read_only_fields = fields
