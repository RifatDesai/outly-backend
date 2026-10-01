import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("category", models.CharField(max_length=80)),
                ("description", models.TextField(max_length=1000)),
                ("visibility", models.CharField(choices=[("PUBLIC", "Public"), ("PRIVATE", "Private")], default="PUBLIC", max_length=10)),
                ("rules", models.TextField(blank=True, max_length=2000)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owned_outly_groups", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="GroupMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("OWNER", "Owner"), ("MODERATOR", "Moderator"), ("MEMBER", "Member")], default="MEMBER", max_length=10)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("REMOVED", "Removed")], default="ACTIVE", max_length=10)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="groups.group")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="outly_group_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["joined_at"]},
        ),
        migrations.CreateModel(
            name="GroupJoinRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("ACCEPTED", "Accepted"), ("REJECTED", "Rejected")], default="PENDING", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="join_requests", to="groups.group")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="outly_group_join_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="GroupPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.CharField(max_length=500)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="outly_group_posts", to=settings.AUTH_USER_MODEL)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="feed_posts", to="groups.group")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(model_name="groupmembership", constraint=models.UniqueConstraint(fields=("group", "user"), name="unique_outly_group_member")),
        migrations.AddConstraint(model_name="groupjoinrequest", constraint=models.UniqueConstraint(fields=("group", "user"), name="unique_outly_group_join_request")),
    ]
