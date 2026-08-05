"""templates/*.json dosyalarını eklentinin ayar biçimine derler.

Kullanım:  python3 build.py
Çıktı:     obsidian-web-clipper-settings.json
"""

import json
import sys
from pathlib import Path

from validate import validate_template

KOK = Path(__file__).resolve().parent
SABLON_DIZINI = KOK / "templates"
CIKTI = KOK / "obsidian-web-clipper-settings.json"

VAULT_ADI = "Aktif Kasa"


def _id_uret(slug):
    """Şablon slug'ından deterministik id üretir.

    Deterministik olması şart: her derlemede aynı id çıkmazsa eklentiye yeniden
    içe aktarım mevcut şablonları güncellemek yerine kopyalarını yaratır.
    """
    return "sbl" + slug.replace("-", "")


def build_settings(sablon_dizini=SABLON_DIZINI):
    sira = json.loads((sablon_dizini / "_order.json").read_text(encoding="utf-8"))

    ayarlar = {
        "template_list": [],
        "vaults": [VAULT_ADI],
        "general_settings": {
            "betaFeatures": False,
            "legacyMode": False,
            "openBehavior": "popup",
            "saveBehavior": "addToObsidian",
            "showMoreActionsButton": False,
            "silentOpen": False,
        },
        "highlighter_settings": {
            "alwaysShowHighlights": True,
            "highlightBehavior": "highlight-inline",
            "highlighterEnabled": True,
        },
        "interpreter_settings": {
            "defaultPromptContext": "",
            "interpreterAutoRun": False,
            "interpreterEnabled": False,
            "interpreterModel": "",
            "models": [],
            "providers": [],
        },
        "reader_settings": {
            "fontSize": 1.5,
            "lineHeight": 1.6,
            "maxWidth": 38,
            "theme": "default",
            "themeMode": "auto",
        },
        "property_types": [],
        "stats": {"addToObsidian": 0, "copyToClipboard": 0, "saveFile": 0, "share": 0},
        "migrationVersion": 1,
    }

    gorulen_props = {}

    for slug in sira:
        yol = sablon_dizini / f"{slug}.json"
        if not yol.exists():
            raise FileNotFoundError(f"_order.json '{slug}' diyor ama {yol} yok")

        tmpl = json.loads(yol.read_text(encoding="utf-8"))

        hatalar = validate_template(tmpl)
        if hatalar:
            raise ValueError(f"{yol.name} kurallara uymuyor:\n  " + "\n  ".join(hatalar))

        tid = _id_uret(slug)
        tmpl["id"] = tid
        for i, prop in enumerate(tmpl.get("properties", [])):
            prop["id"] = f"{tid}p{i}"
            gorulen_props.setdefault(prop["name"], prop.get("type", "text"))

        ayarlar[f"template_{tid}"] = tmpl
        ayarlar["template_list"].append(tid)

    ayarlar["property_types"] = [
        {"name": ad, "type": tur, "defaultValue": ""}
        for ad, tur in sorted(gorulen_props.items())
    ]

    return ayarlar


def main():
    ayarlar = build_settings()
    CIKTI.write_text(
        json.dumps(ayarlar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(ayarlar['template_list'])} şablon derlendi → {CIKTI.name}")


if __name__ == "__main__":
    sys.exit(main())
