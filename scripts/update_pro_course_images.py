#!/usr/bin/env python3
"""
Update course images for 3 pro courses using Unsplash photos.
Run inside CMS container via:
  cat scripts/update_pro_course_images.py | ssh staging-openedx "docker exec -i tutor_local-cms-1 python manage.py cms shell"
"""
import urllib.request
import os

from opaque_keys.edx.keys import CourseKey
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum

store = modulestore()
cs = contentstore()

# Course -> Unsplash photo URL (free, no auth needed for small sizes)
COURSES = {
    "course-v1:MF-MGMT+MF-MGMT-LEADER-2025+2025": {
        "name": "Management et Leadership",
        "url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=560&fit=crop&crop=center",
        "filename": "course_image_leadership.jpg",
    },
    "course-v1:MissionFormations+MF-STRAT-COM-2026+2026": {
        "name": "Strategie Commerciale",
        "url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=560&fit=crop&crop=center",
        "filename": "course_image_stratcom.jpg",
    },
    "course-v1:MissionFormations+scolaire6eme+20266eme": {
        "name": "Scolaire 6eme",
        "url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&h=560&fit=crop&crop=center",
        "filename": "course_image_scolaire.jpg",
    },
}

for course_key_str, info in COURSES.items():
    course_key = CourseKey.from_string(course_key_str)
    course = store.get_course(course_key)
    if not course:
        print(f"  [MISS] {course_key_str} not found")
        continue

    # Download image
    try:
        print(f"  Downloading image for {info['name']}...")
        req = urllib.request.Request(info["url"], headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=30)
        img_data = response.read()
        print(f"    -> {len(img_data)} bytes")
    except Exception as e:
        print(f"  [FAIL] Download failed for {info['name']}: {e}")
        continue

    # Upload as course asset
    asset_key = course_key.make_asset_key("asset", info["filename"])
    content = StaticContent(asset_key, info["filename"], "image/jpeg", img_data)
    cs.save(content)

    # Set as course image
    course.course_image = info["filename"]
    store.update_item(course, ModuleStoreEnum.UserID.mgmt_command)

    print(f"  [OK] {course_key_str} — image mise a jour ({info['name']})")

print("\nTermine.")
