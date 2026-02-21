Mission Theme
#############

This theme is used by the Mission Formations Open edX tenant.

Current customizations:

* LMS footer override: ``lms/templates/footer.html``
* LMS logo override: ``lms/static/images/logo.png``
* LMS style additions: ``lms/static/sass/_extras.scss``

How to enable this theme
========================

1. Enable comprehensive theming in LMS and CMS.
2. Set ``DEFAULT_SITE_THEME`` to ``mission-theme``.
3. Ensure ``COMPREHENSIVE_THEME_DIRS`` contains the parent themes directory.
4. Configure tenant/domain overrides (for example with ``eox-tenant``).

In this repository, a helper script is available at:

``custom-infra/scripts/configure-mission-tenant.sh``

It creates or updates tenant configuration for LMS/CMS routes and applies
the required Mission Formations settings.
