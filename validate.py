"""Web Clipper şablonlarını hedef vault'un kanonik kurallarına göre denetler.

Kural kaynakları:
  Meta/naming-conventions.md, Meta/tag-taxonomy.md, Meta/vault-structure.md
"""

import re

BEKLENEN_PATH = "00 Inbox"
BEKLENEN_BEHAVIOR = "create"
BEKLENEN_TYPE = "referans"

REQUIRED_PROPS = {"type", "date", "created", "tags", "source", "source_type", "title"}

# Meta/tag-taxonomy.md: "İngilizce sistem-tag YASAK"
FORBIDDEN_TAGS = {
    "clipping", "clippings", "article", "articles", "video", "videos",
    "github", "reddit", "twitter", "instagram", "linkedin", "youtube",
    "shopping", "product", "bookmark", "web", "clip",
}

# İzinli: kaynak, kaynak/<alt>, alan/<alt>, eksi
IZINLI_TAG = re.compile(r"^(kaynak(/[a-z0-9-]+)?|alan/[a-z0-9-]+|eksi)$")

AYIRICI = " -- "


def _props(tmpl):
    return {p["name"]: p.get("value", "") for p in tmpl.get("properties", [])}


def validate_template(tmpl):
    """Kural ihlallerini açıklayan string listesi döndürür. Boş liste = geçerli."""
    hatalar = []
    ad = tmpl.get("name", "<isimsiz>")

    if tmpl.get("path") != BEKLENEN_PATH:
        hatalar.append(f"{ad}: path '{tmpl.get('path')}' olmalı '{BEKLENEN_PATH}'")

    if tmpl.get("behavior") != BEKLENEN_BEHAVIOR:
        hatalar.append(f"{ad}: behavior '{BEKLENEN_BEHAVIOR}' olmalı")

    props = _props(tmpl)

    for eksik in sorted(REQUIRED_PROPS - set(props)):
        hatalar.append(f"{ad}: zorunlu alan eksik: {eksik}")

    if "type" in props and props["type"] != BEKLENEN_TYPE:
        hatalar.append(f"{ad}: type '{props['type']}' olmalı '{BEKLENEN_TYPE}'")

    for etiket in [e.strip() for e in props.get("tags", "").split(",") if e.strip()]:
        if etiket in FORBIDDEN_TAGS:
            hatalar.append(f"{ad}: yasaklı İngilizce etiket: {etiket}")
        elif not IZINLI_TAG.match(etiket):
            hatalar.append(f"{ad}: izinsiz etiket biçimi: {etiket}")

    ad_bicimi = tmpl.get("noteNameFormat", "")
    if ad_bicimi.count(AYIRICI) < 2:
        hatalar.append(f"{ad}: dosya adında ' -- ' ayırıcı deseni eksik")
    if re.search(r"safe_name(?!:linux)", ad_bicimi):
        hatalar.append(f"{ad}: safe_name platform belirtmeli (safe_name:linux)")

    # meta: sözdizimi — {{meta:property:og:x}} veya {{meta:name:x}} olmalı
    hepsi = ad_bicimi + tmpl.get("noteContentFormat", "") + "".join(props.values())
    for bulunan in re.findall(r"\{\{meta:([a-z]+):", hepsi):
        if bulunan not in ("property", "name"):
            hatalar.append(
                f"{ad}: eksik meta sözdizimi 'meta:{bulunan}:' — "
                "'meta:property:' veya 'meta:name:' olmalı"
            )

    if "## Notlar" not in tmpl.get("noteContentFormat", ""):
        hatalar.append(f"{ad}: gövdede '## Notlar' bölümü yok")

    return hatalar
