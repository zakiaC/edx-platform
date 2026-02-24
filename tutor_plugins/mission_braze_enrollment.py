"""Tutor plugin: native enrollment confirmation email via Braze.

Goals:
- Keep native Open edX enrollment-email flow (no custom override).
- Wire Braze credentials/canvas id from Tutor config.
- Enable enrollment confirmation flag globally.
"""

from tutor import hooks
from tutor.hooks import priorities


# Config keys managed by Tutor (to be set with `tutor config save --set ...`).
hooks.Filters.CONFIG_DEFAULTS.add_items([
    ("MISSION_BRAZE_API_KEY", ""),
    ("MISSION_BRAZE_API_SERVER", ""),
    ("MISSION_BRAZE_COURSE_ENROLLMENT_CANVAS_ID", ""),
])


# Inject Braze settings into LMS settings.
BRAZE_SETTINGS_PATCH = """
# mission_braze_enrollment: native Open edX enrollment confirmation email via Braze
EDX_BRAZE_API_KEY = "{{ MISSION_BRAZE_API_KEY }}"
EDX_BRAZE_API_SERVER = "{{ MISSION_BRAZE_API_SERVER }}"
BRAZE_COURSE_ENROLLMENT_CANVAS_ID = "{{ MISSION_BRAZE_COURSE_ENROLLMENT_CANVAS_ID }}"
""".strip()

for target in (
    "openedx-lms-common-settings",
    "openedx-lms-production-settings",
    "openedx-lms-development-settings",
):
    hooks.Filters.ENV_PATCHES.add_item((target, BRAZE_SETTINGS_PATCH), priority=priorities.LOW)


# Ensure native enrollment confirmation email flag is enabled.
hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    (
        "lms",
        (
            "./manage.py lms shell -c \"from waffle.models import Flag; "
            "f,_=Flag.objects.get_or_create(name='student.enable_enrollment_confirmation_email'); "
            "f.everyone=True; f.percent=None; f.authenticated=False; f.staff=False; f.superusers=False; f.save()\""
        ),
    ),
    priority=priorities.DEFAULT,
)
