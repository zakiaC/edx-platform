"""
Production asset build settings for Tutor.
Disables JS compression to avoid UglifyJS ES6+ incompatibility.
"""
from cms.envs.production import *  # pylint: disable=wildcard-import

PIPELINE['JS_COMPRESSOR'] = None
