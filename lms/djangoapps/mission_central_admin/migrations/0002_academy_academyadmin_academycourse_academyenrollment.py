import django.db.models.deletion
import django.utils.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("mission_central_admin", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Academy",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("short_name", models.CharField(max_length=30, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("academy_type", models.CharField(choices=[("internal", "Academie MF"), ("b2b", "Entreprise cliente")], default="internal", max_length=10)),
                ("subdomain", models.CharField(blank=True, max_length=100)),
                ("logo", models.ImageField(blank=True, upload_to="academies/logos/")),
                ("primary_color", models.CharField(default="#0965D0", max_length=7)),
                ("secondary_color", models.CharField(default="#01E8AE", max_length=7)),
                ("description", models.TextField(blank=True)),
                ("description_long", models.TextField(blank=True)),
                ("cover_image", models.ImageField(blank=True, upload_to="academies/covers/")),
                ("is_active", models.BooleanField(default=True)),
                ("organization_id", models.CharField(blank=True, max_length=50)),
                ("site_id", models.IntegerField(blank=True, null=True)),
                ("client_name", models.CharField(blank=True, max_length=200)),
                ("client_contact", models.EmailField(blank=True, max_length=254)),
                ("contract_start", models.DateField(blank=True, null=True)),
                ("contract_end", models.DateField(blank=True, null=True)),
                ("max_seats", models.IntegerField(default=0, help_text="0 = illimite")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Academie",
                "verbose_name_plural": "Academies",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="AcademyAdmin",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("super_admin", "Super Admin MF"), ("academy_admin", "Admin Academie"), ("client_admin", "Admin Client B2B")], default="academy_admin", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("academy", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="admins", to="mission_central_admin.academy")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="academy_admin_roles", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Admin Academie",
                "unique_together": {("academy", "user")},
            },
        ),
        migrations.CreateModel(
            name="AcademyCourse",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course_key", models.CharField(max_length=255)),
                ("is_featured", models.BooleanField(default=False)),
                ("order", models.IntegerField(default=0)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("academy", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="courses", to="mission_central_admin.academy")),
            ],
            options={
                "verbose_name": "Cours Academie",
                "ordering": ("order", "-added_at"),
                "unique_together": {("academy", "course_key")},
            },
        ),
        migrations.CreateModel(
            name="AcademyEnrollment",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("enrolled_at", models.DateTimeField(auto_now_add=True)),
                ("academy", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="academy_enrollments", to="mission_central_admin.academy")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="academy_enrollments", to=settings.AUTH_USER_MODEL)),
                ("invited_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("academy", "user")},
            },
        ),
    ]
