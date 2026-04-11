#!/usr/bin/env python3
"""
Generate course card images (SVG) for each of the 24 AJEP courses.
Each image has the subject + level displayed on a Mission-branded gradient.
"""
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ajep_courses", "images")

SUBJECTS = {
    "MATH": {"name": "Mathematiques", "color1": "#0965D0", "color2": "#01E8AE", "icon_path": "M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"},
    "FR": {"name": "Francais", "color1": "#0a1628", "color2": "#0965D0", "icon_path": "M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5V5a2 2 0 012-2h14v14H6.5A2.5 2.5 0 004 19.5z"},
    "ANG": {"name": "Anglais", "color1": "#0965D0", "color2": "#074da0", "icon_path": "M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"},
}

LEVELS = [
    ("CM2", "Primaire"),
    ("6E", "6eme", "College"),
    ("5E", "5eme", "College"),
    ("4E", "4eme", "College"),
    ("3E", "3eme", "College"),
    ("2NDE", "Seconde", "Lycee"),
    ("1ERE", "Premiere", "Lycee"),
    ("TERM", "Terminale", "Lycee"),
]

LEVEL_DISPLAY = {
    "CM2": "CM2", "6E": "6eme", "5E": "5eme", "4E": "4eme",
    "3E": "3eme", "2NDE": "Seconde", "1ERE": "Premiere", "TERM": "Terminale",
}

CYCLE_DISPLAY = {
    "CM2": "Primaire", "6E": "College", "5E": "College", "4E": "College",
    "3E": "College", "2NDE": "Lycee", "1ERE": "Lycee", "TERM": "Lycee",
}


def generate_card_svg(subj_key, level_code):
    subj = SUBJECTS[subj_key]
    level = LEVEL_DISPLAY[level_code]
    cycle = CYCLE_DISPLAY[level_code]
    c1, c2 = subj["color1"], subj["color2"]

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 280">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c1}"/>
      <stop offset="100%" style="stop-color:{c2}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="280" fill="url(#bg)"/>

  <!-- Grid dots -->
  <g opacity="0.1" fill="white">
    <circle cx="20" cy="20" r="1.5"/><circle cx="40" cy="20" r="1.5"/><circle cx="60" cy="20" r="1.5"/>
    <circle cx="20" cy="40" r="1.5"/><circle cx="40" cy="40" r="1.5"/><circle cx="60" cy="40" r="1.5"/>
    <circle cx="340" cy="240" r="1.5"/><circle cx="360" cy="240" r="1.5"/><circle cx="380" cy="240" r="1.5"/>
    <circle cx="340" cy="260" r="1.5"/><circle cx="360" cy="260" r="1.5"/><circle cx="380" cy="260" r="1.5"/>
  </g>

  <!-- Icon -->
  <g transform="translate(30, 80)">
    <path d="{subj['icon_path']}" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.3" transform="scale(2.5)"/>
  </g>

  <!-- Cycle badge -->
  <rect x="200" y="30" width="170" height="28" rx="14" fill="white" opacity="0.15"/>
  <text x="285" y="50" font-family="Ubuntu,Arial,sans-serif" font-size="12" font-weight="700" fill="white" text-anchor="middle" opacity="0.9">{cycle}</text>

  <!-- Level -->
  <text x="195" y="135" font-family="Ubuntu,Arial,sans-serif" font-size="36" font-weight="900" fill="white" text-anchor="start" letter-spacing="-1">{level}</text>

  <!-- Subject -->
  <text x="195" y="168" font-family="Ubuntu,Arial,sans-serif" font-size="16" font-weight="600" fill="white" text-anchor="start" opacity="0.8">{subj['name']}</text>

  <!-- Bottom bar -->
  <rect x="0" y="270" width="400" height="10" fill="white" opacity="0.15"/>

  <!-- AJEP tag -->
  <text x="200" y="250" font-family="Ubuntu,Arial,sans-serif" font-size="11" fill="white" text-anchor="start" opacity="0.5" letter-spacing="1.5">ACADEMIE AJEP</text>
</svg>"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    count = 0
    for level_code in LEVEL_DISPLAY:
        for subj_key in SUBJECTS:
            svg = generate_card_svg(subj_key, level_code)
            filename = f"card_{subj_key}_{level_code}.svg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(svg)
            count += 1
            print(f"  [{count:02d}/24] {filename}")

    print(f"\nTermine: {count} images generees dans {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
