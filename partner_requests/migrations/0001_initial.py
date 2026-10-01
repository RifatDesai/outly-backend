import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="PartnerRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("activity", models.CharField(choices=[("HIKE", "Hike"), ("TRAIL_RUN", "Trail run"), ("CYCLING", "Cycling"), ("CAMPING", "Camping"), ("MEETUP", "Meetup")], max_length=20)),
                ("destination", models.CharField(max_length=200)),
                ("preferred_datetime", models.DateTimeField()),
                ("spots_total", models.PositiveSmallIntegerField(default=1)),
                ("experience_level", models.CharField(choices=[("BEGINNER", "Beginner"), ("INTERMEDIATE", "Intermediate"), ("ADVANCED", "Advanced")], default="BEGINNER", max_length=15)),
                ("description", models.TextField(max_length=1500)),
                ("visibility", models.CharField(choices=[("PUBLIC", "Public"), ("PRIVATE", "Private")], default="PUBLIC", max_length=10)),
                ("status", models.CharField(choices=[("OPEN", "Open"), ("CLOSED", "Closed")], default="OPEN", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="partner_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["preferred_datetime", "-created_at"]},
        ),
        migrations.CreateModel(
            name="PartnerRequestJoin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("ACCEPTED", "Accepted"), ("REJECTED", "Rejected")], default="PENDING", max_length=10)),
                ("message", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="join_requests", to="partner_requests.partnerrequest")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="partner_request_joins", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(model_name="partnerrequestjoin", constraint=models.UniqueConstraint(fields=("request", "user"), name="unique_partner_request_join")),
    ]
