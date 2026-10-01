import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notification_type", models.CharField(choices=[("FOLLOW", "Follow"), ("LIKE", "Like"), ("COMMENT", "Comment"), ("MESSAGE", "Message"), ("GROUP_JOIN", "Group join"), ("GROUP_POST", "Group post"), ("PARTNER_REQUEST", "Partner request"), ("PARTNER_JOIN", "Partner join request"), ("SYSTEM", "System")], default="SYSTEM", max_length=20)),
                ("title", models.CharField(max_length=180)),
                ("body", models.CharField(blank=True, max_length=500)),
                ("target_type", models.CharField(blank=True, max_length=50)),
                ("target_id", models.PositiveBigIntegerField(blank=True, null=True)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="outly_notifications_sent", to=settings.AUTH_USER_MODEL)),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="outly_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
