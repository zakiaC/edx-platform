"""Tutor plugin: publish Mission theme assets at runtime.

Role ownership (single responsibility):
- Static asset publication for mission-theme.
- No auth settings, no route logic.
"""

from tutor import hooks
from tutor.hooks import priorities


hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    (
        "lms",
        "./manage.py lms collectstatic --noinput --no-post-process",
    ),
    priority=priorities.LOW,
)

hooks.Filters.CLI_DO_INIT_TASKS.add_item(
    (
        "lms",
        """
mkdir -p /openedx/staticfiles/css /openedx/staticfiles/js
for file in /openedx/themes/mission-theme/lms/static/css/mf-*.css; do
  [ -f "$file" ] && cp -f "$file" /openedx/staticfiles/css/
done
for file in /openedx/themes/mission-theme/lms/static/js/mf-*.js; do
  [ -f "$file" ] && cp -f "$file" /openedx/staticfiles/js/
done
""".strip(),
    ),
    priority=priorities.LOW + 1,
)
