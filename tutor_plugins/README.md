# Mission Tutor Plugins: Role Ownership Contract

This folder is the source of truth for Mission-specific Tutor plugins.

## One role = one plugin

- `mission_theme_lock.py`
  - Owns auth flow locking and default theme behavior.
  - Owns `/authn* -> /login` caddy redirection and learner-home/authn MFE disablement.
  - Must not own static asset publication.

- `mission_theme_assets.py`
  - Owns theme static publication (`collectstatic` and `mf-*` sync).
  - Must not own auth settings or routing.

- `mission_central_admin.py`
  - Owns central admin app settings and LMS app registration.
  - Must not own theme/auth/csp/certificates policy.

- `mission_braze_enrollment.py`
  - Owns Braze enrollment email settings and related waffle flag.
  - Must not own theme/admin/csp behavior.

- `mission_certificates_policy.py`
  - Owns certificates menu policy setting.
  - Must not own unrelated LMS settings.

- `mission_csp_report_only.py`
  - Owns report-only CSP headers on LMS/CMS caddy.
  - Must not own Django settings unrelated to CSP.

## Deployment rule

Install plugins from this folder only (no drift from `~/Library/Application Support/tutor-plugins`):

```bash
tutor plugins install /root/edx-platform/tutor_plugins/mission_theme_lock.py
tutor plugins install /root/edx-platform/tutor_plugins/mission_theme_assets.py
tutor plugins install /root/edx-platform/tutor_plugins/mission_central_admin.py
tutor plugins install /root/edx-platform/tutor_plugins/mission_braze_enrollment.py
tutor plugins install /root/edx-platform/tutor_plugins/mission_certificates_policy.py
tutor plugins install /root/edx-platform/tutor_plugins/mission_csp_report_only.py
```
