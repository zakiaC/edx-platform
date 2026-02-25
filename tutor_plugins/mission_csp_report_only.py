"""Tutor plugin: CSP header in report-only mode.

Role ownership (single responsibility):
- Add Content-Security-Policy-Report-Only headers on LMS/CMS.
"""

from tutor import hooks
from tutor.hooks import priorities

CSP_REPORT_ONLY_VALUE = (
    "default-src 'self'; "
    "script-src 'self' https: 'report-sample'; "
    "style-src 'self' https: 'unsafe-inline'; "
    "img-src 'self' data: blob: https:; "
    "font-src 'self' data: https:; "
    "connect-src 'self' https: wss:; "
    "frame-ancestors 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self' https:; "
    "report-uri /csp-report"
)

CADDY_CSP_PATCH = f"""
# mission_csp_report_only: monitor CSP violations without blocking traffic
header Content-Security-Policy-Report-Only "{CSP_REPORT_ONLY_VALUE}"
""".strip()

for patch_target in ("caddyfile-lms", "caddyfile-cms"):
    hooks.Filters.ENV_PATCHES.add_item(
        (patch_target, CADDY_CSP_PATCH),
        priority=priorities.DEFAULT,
    )
