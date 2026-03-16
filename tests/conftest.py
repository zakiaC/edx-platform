# -*- coding: utf-8 -*-
"""
Fixtures partagees pour la suite de tests Mission Formations.

Utilisation:
    pytest tests/unit/          # avant chaque commit
    pytest tests/integration/   # avant chaque deploy
    pytest tests/smoke/         # apres chaque deploy
"""
import os
import pathlib

import pytest

# ── Chemins racine ──────────────────────────────────────────────────────────

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
TUTOR_PATCHES_DIR = ROOT_DIR / "tutor-patches"
THEME_DIR = ROOT_DIR / "themes" / "mission-theme"
OLX_DIR = ROOT_DIR / "olx-courses"
PLUGIN_DIR = ROOT_DIR / "lms" / "djangoapps" / "mission_central_admin"
CUSTOM_INFRA_DIR = ROOT_DIR / "custom-infra"
TUTOR_PLUGINS_DIR = ROOT_DIR / "tutor_plugins"

# ── URLs staging ────────────────────────────────────────────────────────────

STAGING_LMS_URL = os.environ.get(
    "MF_LMS_URL", "https://academie.staging.missionformations.com"
)
STAGING_CMS_URL = os.environ.get(
    "MF_CMS_URL", "https://studio.staging.missionformations.com"
)
STAGING_MFE_URL = os.environ.get(
    "MF_MFE_URL", "https://apps.academie.staging.missionformations.com"
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def root_dir():
    return ROOT_DIR


@pytest.fixture
def tutor_patches_dir():
    return TUTOR_PATCHES_DIR


@pytest.fixture
def theme_dir():
    return THEME_DIR


@pytest.fixture
def olx_dir():
    return OLX_DIR


@pytest.fixture
def plugin_dir():
    return PLUGIN_DIR


@pytest.fixture
def staging_urls():
    return {
        "lms": STAGING_LMS_URL,
        "cms": STAGING_CMS_URL,
        "mfe": STAGING_MFE_URL,
    }
