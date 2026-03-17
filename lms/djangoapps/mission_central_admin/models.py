import json

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# ── Modele Academy (multi-academies + B2B) ─────────────────────────────────

class Academy(models.Model):
    ACADEMY_TYPE_INTERNAL = "internal"
    ACADEMY_TYPE_B2B = "b2b"
    ACADEMY_TYPE_CHOICES = (
        (ACADEMY_TYPE_INTERNAL, "Academie MF"),
        (ACADEMY_TYPE_B2B, "Entreprise cliente"),
    )

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    academy_type = models.CharField(
        max_length=10, choices=ACADEMY_TYPE_CHOICES, default=ACADEMY_TYPE_INTERNAL,
    )
    subdomain = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to="academies/logos/", blank=True)
    primary_color = models.CharField(max_length=7, default="#0965D0")
    secondary_color = models.CharField(max_length=7, default="#01E8AE")
    description = models.TextField(blank=True)
    description_long = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="academies/covers/", blank=True)
    is_active = models.BooleanField(default=True)

    # Relations OpenEdX natives
    organization_id = models.CharField(max_length=50, blank=True)
    site_id = models.IntegerField(null=True, blank=True)

    # B2B specifique
    client_name = models.CharField(max_length=200, blank=True)
    client_contact = models.EmailField(blank=True)
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    max_seats = models.IntegerField(default=0, help_text="0 = illimite")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "mission_central_admin"
        ordering = ("name",)
        verbose_name = "Academie"
        verbose_name_plural = "Academies"

    def __str__(self):
        return f"{self.short_name} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.subdomain:
            self.subdomain = self.slug
        super().save(*args, **kwargs)

    @property
    def is_b2b(self):
        return self.academy_type == self.ACADEMY_TYPE_B2B

    @property
    def full_domain(self):
        base = "academie.staging.missionformations.com"
        if self.subdomain:
            return f"{self.subdomain}.{base}"
        return base

    @property
    def seats_used(self):
        return self.academy_enrollments.count()

    @property
    def seats_remaining(self):
        if self.max_seats == 0:
            return None  # illimite
        return max(0, self.max_seats - self.seats_used)


class AcademyAdmin(models.Model):
    ROLE_SUPER_ADMIN = "super_admin"
    ROLE_ACADEMY_ADMIN = "academy_admin"
    ROLE_CLIENT_ADMIN = "client_admin"
    ROLE_CHOICES = (
        (ROLE_SUPER_ADMIN, "Super Admin MF"),
        (ROLE_ACADEMY_ADMIN, "Admin Academie"),
        (ROLE_CLIENT_ADMIN, "Admin Client B2B"),
    )

    academy = models.ForeignKey(
        Academy, on_delete=models.CASCADE, related_name="admins",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="academy_admin_roles",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ACADEMY_ADMIN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "mission_central_admin"
        unique_together = ("academy", "user")
        verbose_name = "Admin Academie"

    def __str__(self):
        return f"{self.user.username} → {self.academy.short_name} ({self.role})"


class AcademyCourse(models.Model):
    academy = models.ForeignKey(
        Academy, on_delete=models.CASCADE, related_name="courses",
    )
    course_key = models.CharField(max_length=255)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "mission_central_admin"
        ordering = ("order", "-added_at")
        unique_together = ("academy", "course_key")
        verbose_name = "Cours Academie"

    def __str__(self):
        return f"{self.academy.short_name} ← {self.course_key}"


class AcademyEnrollment(models.Model):
    """Suivi des inscriptions par academie (pour le compteur de sieges B2B)."""
    academy = models.ForeignKey(
        Academy, on_delete=models.CASCADE, related_name="academy_enrollments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="academy_enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )

    class Meta:
        app_label = "mission_central_admin"
        unique_together = ("academy", "user")

    def __str__(self):
        return f"{self.user.username} @ {self.academy.short_name}"


# ── Modele InternalMessageAudit (existant) ──────────────────────────────────

class InternalMessageAudit(models.Model):
    STATUS_QUEUED = "queued"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_QUEUED, "Queued"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mission_internal_messages",
    )
    recipient_group = models.CharField(max_length=64, db_index=True)
    recipient_count = models.PositiveIntegerField(default=0)
    recipients_json = models.TextField(default="[]")
    subject = models.CharField(max_length=180)
    body = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_QUEUED, db_index=True)
    task_id = models.CharField(max_length=255, blank=True, default="")
    sent_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "mission_central_admin"
        ordering = ("-created",)

    def recipients(self):
        try:
            parsed = json.loads(self.recipients_json or "[]")
        except Exception:  # pylint: disable=broad-except
            return []
        return [str(item).strip().lower() for item in parsed if str(item).strip()]
