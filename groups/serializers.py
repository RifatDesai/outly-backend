from rest_framework import serializers
from .models import Group, GroupMembership, GroupPost, GroupJoinRequest

class GroupSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "category", "description", "visibility", "rules",
                  "owner", "owner_name", "members_count", "my_role", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "owner_name", "members_count", "my_role", "created_at", "updated_at"]

    def get_owner_name(self, obj):
        profile = getattr(obj.owner, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.owner.email

    def get_members_count(self, obj):
        return obj.memberships.filter(status="ACTIVE").count()

    def get_my_role(self, obj):
        user = self.context["request"].user
        membership = obj.memberships.filter(user=user, status="ACTIVE").first()
        return membership.role if membership else None

class GroupMembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    display_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = ["user_id", "display_name", "username", "role", "joined_at"]

    def get_display_name(self, obj):
        profile = getattr(obj.user, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.user.email

    def get_username(self, obj):
        profile = getattr(obj.user, "profile", None)
        return profile.username if profile else ""

class GroupPostSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = GroupPost
        fields = ["id", "group", "author_id", "author_name", "content", "location", "created_at", "updated_at"]
        read_only_fields = ["id", "group", "author_id", "author_name", "created_at", "updated_at"]

    def get_author_name(self, obj):
        profile = getattr(obj.author, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.author.email

class GroupJoinRequestSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = GroupJoinRequest
        fields = ["id", "group", "user_id", "display_name", "status", "created_at", "updated_at"]
        read_only_fields = fields

    def get_display_name(self, obj):
        profile = getattr(obj.user, "profile", None)
        return profile.display_name if profile and profile.display_name else obj.user.email
