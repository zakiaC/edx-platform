"""Fix the scolaire6eme course: rename, update about page, set image."""
import urllib.request

from opaque_keys.edx.keys import CourseKey
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum

store = modulestore()
cs = contentstore()

course_key = CourseKey.from_string("course-v1:MissionFormations+scolaire6eme+20266eme")
course = store.get_course(course_key)

if not course:
    print("Cours non trouve")
else:
    # 1. Rename
    course.display_name = "Scolaire 6eme — Soutien Scolaire"
    course.short_description = "Cours de soutien scolaire niveau 6eme."
    store.update_item(course, ModuleStoreEnum.UserID.mgmt_command)
    print("[OK] Cours renomme: Scolaire 6eme — Soutien Scolaire")

    # 2. Download a better scolaire image
    url = "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&h=560&fit=crop&crop=center"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        img_data = resp.read()
        print(f"  Image telechargee: {len(img_data)} bytes")

        fname = "course_image_scolaire6e.jpg"
        asset_key = course_key.make_asset_key("asset", fname)
        content = StaticContent(asset_key, fname, "image/jpeg", img_data)
        cs.save(content)

        course.course_image = fname
        store.update_item(course, ModuleStoreEnum.UserID.mgmt_command)
        print(f"[OK] Image de couverture mise a jour")
    except Exception as e:
        print(f"[FAIL] Image: {e}")

    # 3. Update about/overview
    overview_html = """
<div style="font-family:'Raleway',Arial,sans-serif;max-width:800px;margin:0 auto;">

  <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;">
    <span style="background:#0965D0;color:white;padding:6px 16px;border-radius:20px;font-size:14px;font-weight:600;">
      Soutien Scolaire
    </span>
    <span style="background:#0a1628;color:white;padding:6px 16px;border-radius:20px;font-size:14px;">
      College — 6eme
    </span>
    <span style="background:#01E8AE;color:#0a1628;padding:6px 16px;border-radius:20px;font-size:14px;font-weight:600;">
      Programme officiel 2025-2026
    </span>
  </div>

  <h2 style="color:#0a1628;font-size:24px;margin-bottom:12px;">
    Soutien Scolaire 6eme
  </h2>
  <p style="color:#555;font-size:16px;line-height:1.7;">
    Ce cours de soutien scolaire est concu pour accompagner les eleves de 6eme
    tout au long de l'annee scolaire. Il couvre les matieres fondamentales
    avec des exercices interactifs et un suivi personnalise.
  </p>

  <h3 style="color:#0965D0;margin-top:32px;margin-bottom:16px;font-size:20px;">
    Notre approche pedagogique
  </h3>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Video-cours</p>
      <p style="font-size:13px;color:#666;margin:0;">Explications claires et visuelles</p>
    </div>
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Exercices interactifs</p>
      <p style="font-size:13px;color:#666;margin:0;">QCM, problemes et cas pratiques</p>
    </div>
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Suivi de progression</p>
      <p style="font-size:13px;color:#666;margin:0;">Tableau de bord en temps reel</p>
    </div>
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Evaluations</p>
      <p style="font-size:13px;color:#666;margin:0;">Bilans trimestriels + examen final</p>
    </div>
  </div>

  <h3 style="color:#0965D0;margin-top:32px;margin-bottom:12px;font-size:20px;">
    Prerequis
  </h3>
  <p style="color:#555;font-size:15px;line-height:1.6;">
    Aucun prerequis particulier. Ce cours est adapte aux eleves de 6eme
    et suit le programme officiel. Un ordinateur ou une tablette avec une connexion internet suffit.
  </p>

  <div style="background:#0a1628;border-radius:12px;padding:24px;margin-top:32px;text-align:center;">
    <p style="color:#01E8AE;font-size:14px;letter-spacing:1px;margin:0 0 4px 0;text-transform:uppercase;">
      Propulse par
    </p>
    <p style="color:white;font-size:22px;font-weight:700;margin:0 0 4px 0;">
      Academie Mission Formations
    </p>
    <p style="color:rgba(255,255,255,0.4);font-size:12px;margin:8px 0 0 0;">
      Soutien scolaire
    </p>
  </div>
</div>
"""
    about_key = course_key.make_usage_key("about", "overview")
    try:
        about_item = store.get_item(about_key)
        about_item.data = overview_html
        store.update_item(about_item, ModuleStoreEnum.UserID.mgmt_command)
    except Exception:
        store.create_item(
            ModuleStoreEnum.UserID.mgmt_command,
            course_key,
            "about",
            block_id="overview",
            fields={"data": overview_html},
        )
    print("[OK] Page About mise a jour")

    # 4. Refresh CourseOverview cache
    from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
    CourseOverview.load_from_module_store(course_key)
    print("[OK] CourseOverview cache rafraichi")

print("\nTermine.")
