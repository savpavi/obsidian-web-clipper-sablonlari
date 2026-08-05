# Web Clipper Şablon Seti — Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Obsidian Web Clipper için, hedef vault'un kanonik kurallarına uyan 10 şablonluk bir set ve bunları tek bir içe-aktarılabilir ayar dosyasına derleyen araç zinciri üretmek.

**Architecture:** Her şablon `templates/` altında ayrı bir JSON dosyası (tek doğruluk kaynağı). `build.py` bunları birleştirip eklentinin beklediği `obsidian-web-clipper-settings.json` biçimine derler. `validate.py` vault kurallarını makine-okunur kurallara çevirir ve testler bunun üzerinden yürür. Şablon içeriği kod değil veri olduğundan TDD şu biçimi alır: önce kuralı denetleyen test yazılır, kural ihlal ettiği için kırmızıya düşer, sonra şablon eklenerek yeşile çekilir.

**Tech Stack:** Python 3 (yalnızca stdlib: `json`, `re`, `pathlib`, `unittest`). Ek bağımlılık yok.

## Global Constraints

Bu kısıtlar her görevin gereksinimlerine örtük olarak dahildir. Kaynak: `docs/superpowers/specs/2026-08-05-obsidian-web-clipper-sablonlari-design.md` ve hedef vault'un `Meta/` dosyaları.

- **Hedef vault:** `~/Documents/Obsidian/Aktif Kasa/`
- **Tüm şablonların `path` değeri:** `00 Inbox`
- **Tüm şablonların `behavior` değeri:** `create`
- **Dosya adı deseni:** `YYYY-MM-DD -- {{Kaynak}} -- {{Başlık}}` — ` -- ` ayırıcısı (boşluk, iki tire, boşluk) zorunlu
- **Zorunlu frontmatter alanları (her şablonda):** `type`, `date`, `created`, `tags`, `source`, `source_type`, `title`
- **`type` değeri her zaman `referans`** — Ekşi Entry dahil (`eksi-baslik` **yasak**, script arşivleriyle çakışır)
- **Yasaklı etiketler:** `clipping`, `clippings`, `article`, `video`, `github`, `reddit`, `twitter`, `shopping` ve diğer İngilizce düz sistem-tag'ler. `Meta/tag-taxonomy.md` açıkça yasaklıyor.
- **İzinli etiket biçimi:** `kaynak` ve `kaynak/<kaynak>`; ek olarak taksonomide zaten var olan `alan/*` ve `eksi`
- **`template_list[0]` = Varsayılan şablon** — eşleşme bulunamazsa `templates[0]` fallback olarak kullanılıyor (`src/core/popup.ts`)
- **`meta:` sözdizimi:** `{{meta:property:og:...}}` — `{{meta:og:...}}` biçimi eksiktir, kullanılmayacak
- **`safe_name` çağrıları platform belirtir:** `|safe_name:linux`
- **Vault dosyalarına doğrudan yazılmaz.** `Meta/tag-taxonomy.md` ve `Meta/naming-conventions.md` için yama hazırlanır, uygulanmaz.
- **Eski `"0"`–`"5"` anahtarları taşınmaz** — ölü veri.

---

## Dosya Yapısı

| Dosya | Sorumluluk |
|---|---|
| `templates/*.json` | Şablon tanımları — tek doğruluk kaynağı, her biri tek bir kaynağı temsil eder |
| `templates/_order.json` | `template_list` sırası; Varsayılan başta |
| `build.py` | `templates/*.json` → `obsidian-web-clipper-settings.json` derlemesi |
| `validate.py` | Vault kurallarını denetleyen saf fonksiyonlar (`validate_template`) |
| `tests/test_validate.py` | `validate.py`'nin kendi testleri |
| `tests/test_templates.py` | Her gerçek şablonu `validate.py`'den geçiren test |
| `obsidian-web-clipper-settings.json` | Üretilen çıktı — elle düzenlenmez |
| `README.md` | Kurulum + bakım rehberi |
| `vault-yamalari.md` | `Meta/` dosyaları için hazırlanan, uygulanmayan yamalar |

---

### Task 1: Doğrulayıcı ve Varsayılan şablon

Kural motorunu ve ilk şablonu birlikte kuruyoruz — doğrulayıcının gerçekten bir şey yakaladığını kanıtlayan en küçük birim.

**Files:**
- Create: `validate.py`
- Create: `tests/test_validate.py`
- Create: `templates/varsayilan.json`
- Create: `tests/test_templates.py`

**Interfaces:**
- Produces: `validate_template(tmpl: dict) -> list[str]` — kural ihlallerini açıklayan string listesi döndürür; boş liste = geçerli. Sonraki tüm görevler bu imzayı kullanır.
- Produces: `REQUIRED_PROPS: set[str]`, `FORBIDDEN_TAGS: set[str]` — modül düzeyi sabitler.

- [ ] **Step 1: Testleri yaz**

`tests/test_validate.py`:

```python
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validate import validate_template


def gecerli_sablon():
    """Tüm kuralları sağlayan asgari şablon."""
    return {
        "schemaVersion": "0.1.0",
        "name": "Deneme",
        "behavior": "create",
        "path": "00 Inbox",
        "noteNameFormat": '{{date|date:"YYYY-MM-DD"}} -- Deneme -- {{title|safe_name:linux|slice:0,60}}',
        "noteContentFormat": "{{content}}\n\n## Notlar\n\n",
        "triggers": [],
        "properties": [
            {"name": "type", "value": "referans", "type": "text"},
            {"name": "date", "value": '{{date|date:"YYYY-MM-DD"}}', "type": "date"},
            {"name": "created", "value": '{{date|date:"YYYY-MM-DD"}}', "type": "date"},
            {"name": "tags", "value": "kaynak", "type": "multitext"},
            {"name": "source", "value": "{{url}}", "type": "text"},
            {"name": "source_type", "value": "deneme", "type": "text"},
            {"name": "title", "value": "{{title}}", "type": "text"},
        ],
    }


class ValidateTemplateTest(unittest.TestCase):
    def test_gecerli_sablon_hata_vermez(self):
        self.assertEqual(validate_template(gecerli_sablon()), [])

    def test_yanlis_path_yakalanir(self):
        t = gecerli_sablon()
        t["path"] = "Clippings/Articles"
        self.assertIn("path", " ".join(validate_template(t)))

    def test_eksik_zorunlu_alan_yakalanir(self):
        t = gecerli_sablon()
        t["properties"] = [p for p in t["properties"] if p["name"] != "source_type"]
        self.assertIn("source_type", " ".join(validate_template(t)))

    def test_type_referans_degilse_yakalanir(self):
        t = gecerli_sablon()
        for p in t["properties"]:
            if p["name"] == "type":
                p["value"] = "eksi-baslik"
        self.assertIn("type", " ".join(validate_template(t)))

    def test_ingilizce_tag_yakalanir(self):
        t = gecerli_sablon()
        for p in t["properties"]:
            if p["name"] == "tags":
                p["value"] = "clipping, youtube"
        hatalar = " ".join(validate_template(t))
        self.assertIn("clipping", hatalar)

    def test_izinsiz_tag_bicimi_yakalanir(self):
        t = gecerli_sablon()
        for p in t["properties"]:
            if p["name"] == "tags":
                p["value"] = "kaynak, rastgele-etiket"
        self.assertIn("rastgele-etiket", " ".join(validate_template(t)))

    def test_ayirici_olmayan_dosya_adi_yakalanir(self):
        t = gecerli_sablon()
        t["noteNameFormat"] = '{{date|date:"YYYY-MM-DD"}} YT {{title}}'
        self.assertIn("ayırıcı", " ".join(validate_template(t)))

    def test_eksik_meta_property_yakalanir(self):
        t = gecerli_sablon()
        t["noteContentFormat"] = "{{meta:og:site_name}}"
        self.assertIn("meta:property:", " ".join(validate_template(t)))

    def test_platformsuz_safe_name_yakalanir(self):
        t = gecerli_sablon()
        t["noteNameFormat"] = '{{date|date:"YYYY-MM-DD"}} -- Deneme -- {{title|safe_name}}'
        self.assertIn("safe_name", " ".join(validate_template(t)))

    def test_notlar_bolumu_yoksa_yakalanir(self):
        t = gecerli_sablon()
        t["noteContentFormat"] = "{{content}}"
        self.assertIn("Notlar", " ".join(validate_template(t)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Testin kırmızıya düştüğünü gör**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -m unittest tests.test_validate -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'validate'`

- [ ] **Step 3: `validate.py`'yi yaz**

```python
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
    if "safe_name" in ad_bicimi and "safe_name:" not in ad_bicimi:
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
```

- [ ] **Step 4: Testin yeşile döndüğünü gör**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -m unittest tests.test_validate -v`
Expected: PASS — 10 test

- [ ] **Step 5: Şablon test koşucusunu yaz**

`tests/test_templates.py`:

```python
import json, sys, unittest
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
from validate import validate_template

SABLON_DIZINI = KOK / "templates"


class TemplatesTest(unittest.TestCase):
    def test_tum_sablonlar_kurallara_uyar(self):
        dosyalar = sorted(p for p in SABLON_DIZINI.glob("*.json") if not p.name.startswith("_"))
        self.assertTrue(dosyalar, "templates/ altında şablon yok")

        tum_hatalar = []
        for yol in dosyalar:
            tmpl = json.loads(yol.read_text(encoding="utf-8"))
            tum_hatalar += [f"{yol.name}: {h}" for h in validate_template(tmpl)]

        self.assertEqual(tum_hatalar, [], "\n" + "\n".join(tum_hatalar))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 6: Şablon testinin kırmızıya düştüğünü gör**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -m unittest tests.test_templates -v`
Expected: FAIL — `AssertionError: templates/ altında şablon yok`

- [ ] **Step 7: Varsayılan şablonu yaz**

`templates/varsayilan.json`:

```json
{
  "schemaVersion": "0.1.0",
  "name": "Varsayılan",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": [],
  "noteNameFormat": "{{date|date:\"YYYY-MM-DD\"}} -- Klip -- {{title|safe_name:linux|slice:0,60}}",
  "noteContentFormat": "{{highlights|map: item => item.content|join:\"\\n\\n\"|markdown|callout:(\"quote\", \"Vurgular\")}}\n\n{{content}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "klip", "type": "text"},
    {"name": "title", "value": "{{title}}", "type": "text"},
    {"name": "author", "value": "{{author}}", "type": "multitext"},
    {"name": "site", "value": "{{site}}", "type": "text"},
    {"name": "description", "value": "{{description|slice:0,300}}", "type": "text"}
  ]
}
```

- [ ] **Step 8: Şablon testinin yeşile döndüğünü gör**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -m unittest discover tests -v`
Expected: PASS — tüm testler

- [ ] **Step 9: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add validate.py tests/ templates/varsayilan.json
git commit -m "feat: kural doğrulayıcı ve Varsayılan şablon"
```

---

### Task 2: Derleme betiği

10 şablonu eklentinin beklediği tek ayar dosyasına çeviren araç. Varsayılan'ın listede ilk sırada olmasını burada garanti ediyoruz.

**Files:**
- Create: `build.py`
- Create: `templates/_order.json`
- Create: `tests/test_build.py`

**Interfaces:**
- Consumes: `templates/*.json` (Task 1'den), `validate_template` (Task 1'den)
- Produces: `build_settings(sablon_dizini: Path) -> dict` — tam ayar sözlüğü döndürür
- Produces: `templates/_order.json` — dosya adı (uzantısız) listesi; sıralamanın tek kaynağı

- [ ] **Step 1: Testi yaz**

`tests/test_build.py`:

```python
import sys, unittest
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
from build import build_settings

SABLON_DIZINI = KOK / "templates"


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.ayarlar = build_settings(SABLON_DIZINI)

    def test_varsayilan_listenin_basinda(self):
        """templates[0] fallback olarak kullanılıyor (src/core/popup.ts)."""
        ilk_id = self.ayarlar["template_list"][0]
        self.assertEqual(self.ayarlar[f"template_{ilk_id}"]["name"], "Varsayılan")

    def test_her_sablonun_id_si_benzersiz(self):
        idler = self.ayarlar["template_list"]
        self.assertEqual(len(idler), len(set(idler)))

    def test_template_list_ile_anahtarlar_ortusuyor(self):
        anahtar_idler = {k[len("template_"):] for k in self.ayarlar if k.startswith("template_")}
        self.assertEqual(anahtar_idler, set(self.ayarlar["template_list"]))

    def test_olu_sayisal_anahtarlar_yok(self):
        """Eski dosyadaki '0'-'5' artıkları taşınmamalı."""
        for k in self.ayarlar:
            self.assertFalse(k.isdigit(), f"ölü sayısal anahtar: {k}")

    def test_vault_adi_ayarli(self):
        self.assertEqual(self.ayarlar["vaults"], ["Aktif Kasa"])

    def test_interpreter_kapali(self):
        self.assertFalse(self.ayarlar["interpreter_settings"]["interpreterEnabled"])

    def test_uretilen_sablonlarda_id_alani_var(self):
        for tid in self.ayarlar["template_list"]:
            self.assertEqual(self.ayarlar[f"template_{tid}"]["id"], tid)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Testin kırmızıya düştüğünü gör**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -m unittest tests.test_build -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build'`

- [ ] **Step 3: Sıra dosyasını yaz**

`templates/_order.json` — Varsayılan başta olmak zorunda; kalanların sırası yalnızca aynı kademedeki tetikleyiciler için önemli (Ürün, Makale'den önce).

```json
[
  "varsayilan",
  "eksi-entry",
  "youtube",
  "github",
  "x",
  "reddit",
  "instagram",
  "linkedin",
  "urun",
  "makale"
]
```

- [ ] **Step 4: `build.py`'yi yaz**

```python
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
```

- [ ] **Step 5: Eksik şablonlar yüzünden hata verdiğini doğrula**

Şu an yalnızca `varsayilan.json` var; `_order.json` 10 tane bekliyor.

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 build.py`
Expected: FAIL — `FileNotFoundError: _order.json 'eksi-entry' diyor ama ... yok`

- [ ] **Step 6: `_order.json`'ı geçici olarak tek şablona indir**

Kalan 9 satırı sil, yalnızca `["varsayilan"]` bırak. Sonraki görevlerde her şablon eklendikçe kendi satırı geri konacak.

- [ ] **Step 7: Testlerin yeşile döndüğünü gör**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 build.py && python3 -m unittest discover tests -v`
Expected: PASS — `1 şablon derlendi` + tüm testler geçer

- [ ] **Step 8: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add build.py templates/_order.json tests/test_build.py obsidian-web-clipper-settings.json
git commit -m "feat: şablon derleme betiği"
```

---

### Task 3: Makale ve Ekşi Entry

**Files:**
- Create: `templates/makale.json`
- Create: `templates/eksi-entry.json`
- Modify: `templates/_order.json`

**Interfaces:**
- Consumes: `validate_template` (Task 1), `build_settings` (Task 2)

- [ ] **Step 1: Makale şablonunu yaz**

`templates/makale.json`:

```json
{
  "schemaVersion": "0.1.0",
  "name": "Makale",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": [
    "schema:@Article",
    "schema:@NewsArticle",
    "schema:@BlogPosting",
    "schema:@TechArticle"
  ],
  "noteNameFormat": "{{published|date:\"YYYY-MM-DD\"}} -- Makale -- {{title|safe_name:linux|slice:0,60}}",
  "noteContentFormat": "{{highlights|map: item => item.content|join:\"\\n\\n\"|markdown|callout:(\"quote\", \"Vurgular\")}}\n\n{{content}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{published|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/makale", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "makale", "type": "text"},
    {"name": "title", "value": "{{title}}", "type": "text"},
    {"name": "author", "value": "{{author}}", "type": "multitext"},
    {"name": "site", "value": "{{site}}", "type": "text"},
    {"name": "description", "value": "{{description|slice:0,300}}", "type": "text"},
    {"name": "words", "value": "{{words}}", "type": "number"}
  ]
}
```

- [ ] **Step 2: Ekşi Entry şablonunu yaz**

`templates/eksi-entry.json` — `type` **`referans`**, `eksi-baslik` değil. Script arşivleriyle çakışmasın diye ayırt edici alan `source_type: eksi-entry`.

```json
{
  "schemaVersion": "0.1.0",
  "name": "Ekşi Entry",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": ["/^https:\\/\\/eksisozluk\\.com\\/entry\\/\\d+/"],
  "noteNameFormat": "{{date|date:\"YYYY-MM-DD\"}} -- Eksi Entry -- {{title|split:\" - ekşi sözlük\"|first|safe_name:linux|slice:0,60}}",
  "noteContentFormat": "> **{{title|split:\" - ekşi sözlük\"|first}}** · {{selector:a.entry-author|first}}\n\n{{selectorHtml:#entry-item-list li div.content|first|markdown|blockquote}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/eksi, eksi", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "eksi-entry", "type": "text"},
    {"name": "title", "value": "{{title|split:\" - ekşi sözlük\"|first}}", "type": "text"},
    {"name": "baslik", "value": "{{title|split:\" - ekşi sözlük\"|first}}", "type": "text"},
    {"name": "yazar", "value": "{{selector:a.entry-author|first}}", "type": "text"},
    {"name": "entry_id", "value": "{{url|split:\"/entry/\"|last}}", "type": "text"},
    {"name": "moc", "value": "[[Eksi Kaynaklari MOC]]", "type": "text"}
  ]
}
```

- [ ] **Step 3: `_order.json`'a ekle**

```json
["varsayilan", "eksi-entry", "makale"]
```

- [ ] **Step 4: Doğrula ve derle**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 build.py && python3 -m unittest discover tests -v`
Expected: PASS — `3 şablon derlendi`

- [ ] **Step 5: Ekşi ayrımını gözle doğrula**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -c "import json;d=json.load(open('templates/eksi-entry.json'));p={x['name']:x['value'] for x in d['properties']};print('type =',p['type']);print('source_type =',p['source_type'])"`
Expected: `type = referans` ve `source_type = eksi-entry` — `eksi-baslik` **görülmemeli**

- [ ] **Step 6: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add templates/ obsidian-web-clipper-settings.json
git commit -m "feat: Makale ve Ekşi Entry şablonları"
```

---

### Task 4: YouTube ve GitHub

**Files:**
- Create: `templates/youtube.json`
- Create: `templates/github.json`
- Modify: `templates/_order.json`

- [ ] **Step 1: YouTube şablonunu yaz**

`templates/youtube.json` — süre için doğrulanmış `|duration` filtresi kullanılıyor (eski `|replace` zincirinin yerine).

```json
{
  "schemaVersion": "0.1.0",
  "name": "YouTube Video",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": [
    "https://www.youtube.com/watch",
    "https://m.youtube.com/watch",
    "https://youtu.be/"
  ],
  "noteNameFormat": "{{schema:@VideoObject:uploadDate|date:\"YYYY-MM-DD\"}} -- YouTube -- {{schema:@VideoObject:name|safe_name:linux|slice:0,60}}",
  "noteContentFormat": "![video]({{url}})\n\n---\n\n## Açıklama\n\n{{schema:@VideoObject:description|slice:0,2000|trim}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{schema:@VideoObject:uploadDate|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/youtube", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "youtube", "type": "text"},
    {"name": "title", "value": "{{schema:@VideoObject:name}}", "type": "text"},
    {"name": "channel", "value": "{{schema:@VideoObject:author}}", "type": "text"},
    {"name": "duration", "value": "{{schema:@VideoObject:duration|duration:\"HH:mm:ss\"}}", "type": "text"},
    {"name": "author", "value": "{{schema:@VideoObject:author}}", "type": "multitext"}
  ]
}
```

- [ ] **Step 2: GitHub şablonunu yaz**

`templates/github.json` — regex yalnızca repo kökünü yakalar, alt sayfaları değil. Yıldız sayısı DOM'dan; kırılganlık README'ye not düşülecek.

```json
{
  "schemaVersion": "0.1.0",
  "name": "GitHub Repo",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": ["/^https:\\/\\/github\\.com\\/[\\w.-]+\\/[\\w.-]+\\/?$/"],
  "noteNameFormat": "{{date|date:\"YYYY-MM-DD\"}} -- GitHub -- {{url|split:\"github.com/\"|last|replace:\"/\":\"-\"|safe_name:linux|slice:0,60}}",
  "noteContentFormat": "> {{meta:property:og:description|slice:0,300}}\n\n---\n\n{{content}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/github, alan/teknik", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "github", "type": "text"},
    {"name": "title", "value": "{{title|split:\" · GitHub\"|first}}", "type": "text"},
    {"name": "repo", "value": "{{url|split:\"github.com/\"|last}}", "type": "text"},
    {"name": "stars", "value": "{{selector:#repo-stars-counter-star}}", "type": "text"},
    {"name": "description", "value": "{{meta:property:og:description|slice:0,300}}", "type": "text"}
  ]
}
```

- [ ] **Step 3: `_order.json`'a ekle**

```json
["varsayilan", "eksi-entry", "youtube", "github", "makale"]
```

- [ ] **Step 4: Doğrula ve derle**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 build.py && python3 -m unittest discover tests -v`
Expected: PASS — `5 şablon derlendi`

- [ ] **Step 5: GitHub regex'ini test et**

Run:
```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -c "
import re
d = re.compile(r'^https://github\.com/[\w.-]+/[\w.-]+/?$')
for u, beklenen in [
    ('https://github.com/obsidianmd/obsidian-clipper', True),
    ('https://github.com/obsidianmd/obsidian-clipper/', True),
    ('https://github.com/obsidianmd/obsidian-clipper/issues/689', False),
    ('https://github.com/obsidianmd', False),
]:
    sonuc = bool(d.match(u))
    print('OK ' if sonuc == beklenen else 'HATA', u, sonuc)
"
```
Expected: dört satır da `OK` ile başlamalı

- [ ] **Step 6: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add templates/ obsidian-web-clipper-settings.json
git commit -m "feat: YouTube ve GitHub şablonları"
```

---

### Task 5: X ve Reddit

**Files:**
- Create: `templates/x.json`
- Create: `templates/reddit.json`
- Modify: `templates/_order.json`

- [ ] **Step 1: X şablonunu yaz**

`templates/x.json` — handle URL'den ayrıştırılıyor: `https://x.com/handle/status/123` bölününce `["https:", "", "x.com", "handle", "status", "123"]`, yani `slice:3,-2` → `["handle"]`.

```json
{
  "schemaVersion": "0.1.0",
  "name": "X (Twitter) Post",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": [
    "/^https:\\/\\/x\\.com\\/[A-Za-z0-9_]+\\/status\\/\\d+/",
    "/^https:\\/\\/twitter\\.com\\/[A-Za-z0-9_]+\\/status\\/\\d+/"
  ],
  "noteNameFormat": "{{published|date:\"YYYY-MM-DD\"}} -- X -- {{url|split:\"/\"|slice:3,-2|first|safe_name:linux}}",
  "noteContentFormat": "![tweet]({{url}})\n\n---\n\n{{title|split:\" on X: \"|last|slice:1,-5|remove_html|trim}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{published|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/x", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "x", "type": "text"},
    {"name": "title", "value": "{{title|split:\" on X: \"|first}}", "type": "text"},
    {"name": "author", "value": "{{title|split:\" on X: \"|first}}", "type": "multitext"},
    {"name": "handle", "value": "@{{url|split:\"/\"|slice:3,-2|first}}", "type": "text"}
  ]
}
```

- [ ] **Step 2: Reddit şablonunu yaz**

`templates/reddit.json` — `shreddit-*` seçicileri canlı testte doğrulanacak (Task 9).

```json
{
  "schemaVersion": "0.1.0",
  "name": "Reddit Post",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": ["/^https:\\/\\/(www|old)\\.reddit\\.com\\/r\\/\\w+\\/comments\\//"],
  "noteNameFormat": "{{selector:shreddit-post?created-timestamp|date:\"YYYY-MM-DD\"}} -- Reddit -- {{selector:shreddit-post?post-title|safe_name:linux|slice:0,60}}",
  "noteContentFormat": "> **{{selector:shreddit-post?subreddit-prefixed-name}}** · u/{{selector:shreddit-post?author}} · ⬆️ {{selector:shreddit-post?score}}\n\n---\n\n{{selectorHtml:shreddit-post div[slot=\"text-body\"]|markdown|trim}}\n\n---\n\n### İlk Yorum\n\n**{{selector:shreddit-comment?author|first}}**\n\n{{selectorHtml:shreddit-comment div[slot=\"comment\"]|first|markdown|blockquote}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{selector:shreddit-post?created-timestamp|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/reddit", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "reddit", "type": "text"},
    {"name": "title", "value": "{{selector:shreddit-post?post-title|trim}}", "type": "text"},
    {"name": "subreddit", "value": "{{selector:shreddit-post?subreddit-prefixed-name}}", "type": "text"},
    {"name": "author", "value": "u/{{selector:shreddit-post?author}}", "type": "multitext"},
    {"name": "score", "value": "{{selector:shreddit-post?score}}", "type": "number"}
  ]
}
```

- [ ] **Step 3: `_order.json`'a ekle**

```json
["varsayilan", "eksi-entry", "youtube", "github", "x", "reddit", "makale"]
```

- [ ] **Step 4: Doğrula ve derle**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 build.py && python3 -m unittest discover tests -v`
Expected: PASS — `7 şablon derlendi`

- [ ] **Step 5: X handle ayrıştırmasını test et**

Run:
```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -c "
for u in ['https://x.com/kepano/status/1234567890',
          'https://twitter.com/obsdmd/status/999']:
    print(u, '->', u.split('/')[3:-2])
"
```
Expected: `['kepano']` ve `['obsdmd']`

- [ ] **Step 6: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add templates/ obsidian-web-clipper-settings.json
git commit -m "feat: X ve Reddit şablonları"
```

---

### Task 6: Instagram ve LinkedIn

Setin en kırılgan iki şablonu. İkisi de login duvarı arkasında; veri `og:` meta etiketlerinden çekiliyor çünkü DOM class isimleri sürekli değişiyor.

**Files:**
- Create: `templates/instagram.json`
- Create: `templates/linkedin.json`
- Modify: `templates/_order.json`

- [ ] **Step 1: Instagram şablonunu yaz**

`templates/instagram.json` — kullanıcı adı URL'de **yok** (`instagram.com/p/KOD/`), bu yüzden `og:title`'dan ayrıştırılıyor.

```json
{
  "schemaVersion": "0.1.0",
  "name": "Instagram Post",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": ["/^https:\\/\\/(www\\.)?instagram\\.com\\/(p|reel)\\//"],
  "noteNameFormat": "{{date|date:\"YYYY-MM-DD\"}} -- Instagram -- {{meta:property:og:title|split:\" on Instagram\"|first|safe_name:linux|slice:0,40}}",
  "noteContentFormat": "{{image|image:\"kapak\"}}\n\n---\n\n{{meta:property:og:description|trim}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/instagram", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "instagram", "type": "text"},
    {"name": "title", "value": "{{meta:property:og:title|split:\" on Instagram\"|first}}", "type": "text"},
    {"name": "author", "value": "{{meta:property:og:title|split:\" on Instagram\"|first}}", "type": "multitext"},
    {"name": "image", "value": "{{image}}", "type": "text"}
  ]
}
```

- [ ] **Step 2: LinkedIn şablonunu yaz**

`templates/linkedin.json` — regex yalnızca `/posts/` ve `/feed/update/` yakalar. `/pulse/` **bilerek dışarıda**: o sayfalar `@Article` şeması taşıdığı için Makale şablonuna düşer ve tam metin muamelesi görür.

```json
{
  "schemaVersion": "0.1.0",
  "name": "LinkedIn Gönderi",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": [
    "/^https:\\/\\/(www\\.)?linkedin\\.com\\/posts\\//",
    "/^https:\\/\\/(www\\.)?linkedin\\.com\\/feed\\/update\\//"
  ],
  "noteNameFormat": "{{date|date:\"YYYY-MM-DD\"}} -- LinkedIn -- {{meta:property:og:title|split:\" on LinkedIn\"|first|safe_name:linux|slice:0,40}}",
  "noteContentFormat": "{{content}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/linkedin", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "linkedin", "type": "text"},
    {"name": "title", "value": "{{meta:property:og:title|split:\" on LinkedIn\"|first}}", "type": "text"},
    {"name": "author", "value": "{{meta:property:og:title|split:\" on LinkedIn\"|first}}", "type": "multitext"},
    {"name": "description", "value": "{{meta:property:og:description|slice:0,300}}", "type": "text"}
  ]
}
```

- [ ] **Step 3: `_order.json`'a ekle**

```json
["varsayilan", "eksi-entry", "youtube", "github", "x", "reddit", "instagram", "linkedin", "makale"]
```

- [ ] **Step 4: Doğrula ve derle**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 build.py && python3 -m unittest discover tests -v`
Expected: PASS — `9 şablon derlendi`

- [ ] **Step 5: LinkedIn regex'inin `/pulse/` yakalamadığını doğrula**

Run:
```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -c "
import re
d = [re.compile(r'^https://(www\.)?linkedin\.com/posts/'),
     re.compile(r'^https://(www\.)?linkedin\.com/feed/update/')]
for u, beklenen in [
    ('https://www.linkedin.com/posts/biri_gonderi-activity-123', True),
    ('https://www.linkedin.com/feed/update/urn:li:activity:123', True),
    ('https://www.linkedin.com/pulse/uzun-makale-biri', False),
]:
    sonuc = any(x.match(u) for x in d)
    print('OK ' if sonuc == beklenen else 'HATA', u, sonuc)
"
```
Expected: üç satır da `OK` ile başlamalı — `/pulse/` **eşleşmemeli**

- [ ] **Step 6: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add templates/ obsidian-web-clipper-settings.json
git commit -m "feat: Instagram ve LinkedIn şablonları"
```

---

### Task 7: Ürün şablonu

Setin son şablonu. `@Product` şeması yayınlayan her mağazada çalışır (Amazon, Trendyol, Hepsiburada dahil).

**Files:**
- Create: `templates/urun.json`
- Modify: `templates/_order.json`

- [ ] **Step 1: Ürün şablonunu yaz**

`templates/urun.json` — iç içe şema erişimi (`offers:price`) canlı testte doğrulanacak (Task 9).

```json
{
  "schemaVersion": "0.1.0",
  "name": "Ürün",
  "behavior": "create",
  "path": "00 Inbox",
  "context": "",
  "triggers": ["schema:@Product"],
  "noteNameFormat": "{{date|date:\"YYYY-MM-DD\"}} -- Urun -- {{schema:@Product:name|safe_name:linux|slice:0,60}}",
  "noteContentFormat": "{{schema:@Product:image|first|image:\"ürün\"}}\n\n---\n\n## Detaylar\n\n| | |\n|---|---|\n| **Fiyat** | {{schema:@Product:offers:price}} {{schema:@Product:offers:priceCurrency}} |\n| **Mağaza** | {{site}} |\n| **Marka** | {{schema:@Product:brand:name}} |\n| **Durum** | {{schema:@Product:offers:availability|replace:\"https://schema.org/\":\"\"}} |\n| **Puan** | {{schema:@Product:aggregateRating:ratingValue}}/5 ({{schema:@Product:aggregateRating:reviewCount}} değerlendirme) |\n\n## Açıklama\n\n{{schema:@Product:description|slice:0,1000|trim}}\n\n---\n\n## Notlar\n\n",
  "properties": [
    {"name": "type", "value": "referans", "type": "text"},
    {"name": "date", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "created", "value": "{{date|date:\"YYYY-MM-DD\"}}", "type": "date"},
    {"name": "tags", "value": "kaynak, kaynak/urun", "type": "multitext"},
    {"name": "source", "value": "{{url}}", "type": "text"},
    {"name": "source_type", "value": "urun", "type": "text"},
    {"name": "title", "value": "{{schema:@Product:name}}", "type": "text"},
    {"name": "price", "value": "{{schema:@Product:offers:price}}", "type": "text"},
    {"name": "currency", "value": "{{schema:@Product:offers:priceCurrency}}", "type": "text"},
    {"name": "store", "value": "{{site}}", "type": "text"},
    {"name": "brand", "value": "{{schema:@Product:brand:name}}", "type": "text"},
    {"name": "rating", "value": "{{schema:@Product:aggregateRating:ratingValue}}", "type": "text"},
    {"name": "availability", "value": "{{schema:@Product:offers:availability|replace:\"https://schema.org/\":\"\"}}", "type": "text"},
    {"name": "image", "value": "{{schema:@Product:image|first}}", "type": "text"}
  ]
}
```

- [ ] **Step 2: `_order.json`'ı tamamla**

Ürün, Makale'den **önce** gelmeli: ikisi de şema kademesinde, bir sayfa hem `@Product` hem `@Article` yayınlarsa liste sırası belirleyici olur.

```json
[
  "varsayilan",
  "eksi-entry",
  "youtube",
  "github",
  "x",
  "reddit",
  "instagram",
  "linkedin",
  "urun",
  "makale"
]
```

- [ ] **Step 3: Doğrula ve derle**

Run: `cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 build.py && python3 -m unittest discover tests -v`
Expected: PASS — `10 şablon derlendi`

- [ ] **Step 4: Varsayılan'ın hâlâ listenin başında olduğunu doğrula**

Run:
```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper" && python3 -c "
import json
d = json.load(open('obsidian-web-clipper-settings.json'))
ilk = d['template_list'][0]
print('template_list[0] =', d['template_' + ilk]['name'])
print('toplam:', len(d['template_list']))
"
```
Expected: `template_list[0] = Varsayılan` ve `toplam: 10`

- [ ] **Step 5: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add templates/ obsidian-web-clipper-settings.json
git commit -m "feat: Ürün şablonu — set tamamlandı"
```

---

### Task 8: README ve vault yamaları

**Files:**
- Create: `README.md`
- Create: `vault-yamalari.md`

- [ ] **Step 1: `README.md`'yi yaz**

Şu bölümleri içermeli:

1. **Ne bu** — 10 şablonluk set, hedef vault `~/Documents/Obsidian/Aktif Kasa/`, hepsi `00 Inbox`'a yazar
2. **Kurulum** — Web Clipper ayarları → Import → `obsidian-web-clipper-settings.json` seç. Uyarı: bu **tüm** ayarları değiştirir; tek şablon eklemek için `templates/<ad>.json` dosyasını tek tek import et.
3. **Şablon tablosu** — ad, tetikleyici, ürettiği dosya adı örneği
4. **Eşleşme mekaniği** — üç kademe (URL öneki → regex → şema), `template_list[0]` fallback. Kaynak: `src/utils/triggers.ts`, `src/core/popup.ts`
5. **Kırılganlık haritası** — hangi şablon neye bağlı:

   | Şablon | Bağımlılık | Bozulursa |
   |---|---|---|
   | YouTube, Ürün, Makale | schema.org JSON-LD | Nadiren bozulur; site şemayı kaldırırsa |
   | GitHub | `og:` meta + `#repo-stars-counter-star` | Yıldız sayısı boş kalır, gerisi çalışır |
   | Reddit | `shreddit-*` web component'leri | Reddit arayüz değiştirince tamamen boşalır |
   | X | Sayfa başlığı ayrıştırma | Başlık biçimi değişirse metin bozulur |
   | Instagram, LinkedIn | `og:` meta | Login duvarı; çıkış yapmışken boş gelebilir |

6. **Bakım** — şablon düzenle → `python3 build.py` → `python3 -m unittest discover tests` → yeniden import et. `obsidian-web-clipper-settings.json` **elle düzenlenmez**, üretilir.
7. **Canlı test sonuçları** — Task 9'da doldurulacak boş tablo

- [ ] **Step 2: `vault-yamalari.md`'yi yaz**

İki yama içerir, **uygulanmaz** — kullanıcı onayıyla işlenir.

`Meta/tag-taxonomy.md` için, "LLM Sohbet Kaynaklari" bölümünün ardına:

```markdown
## Web Clipper Kaynaklari

#kaynak/makale #kaynak/youtube #kaynak/github #kaynak/x #kaynak/instagram
#kaynak/linkedin #kaynak/reddit #kaynak/urun #kaynak/eksi

> **Not (2026-08-05):** Obsidian Web Clipper sablonlarinin urettigi klip
> notlari icin kaynak etiketleri. Mevcut `#kaynak/claude`, `#kaynak/chatgpt`,
> `#kaynak/gemini` deseninin devami. Tum klip notlari `type: referans` ve
> `source_type: <kaynak>` frontmatter alanlarini tasir; ayrica Ingilizce duz
> sistem-tag (`#clipping`, `#article`, `#video`) KULLANILMAZ.
```

`Meta/naming-conventions.md` için, "Dosyalar" bölümündeki Tip listesinin ardına:

```markdown
**Web Clipper Tip degerleri (2026-08-05):**
`YouTube`, `GitHub`, `X`, `Reddit`, `Instagram`, `LinkedIn`, `Urun`,
`Makale`, `Eksi Entry`, `Klip`

Ornek: `2026-08-05 -- YouTube -- Fedora Kurulum Rehberi.md`

`Klip`, hicbir sablonun tetikleyicisi eslesmediginde devreye giren
Varsayilan sablonun Tip degeridir.
```

- [ ] **Step 3: Commit**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
git add README.md vault-yamalari.md
git commit -m "docs: kurulum rehberi ve vault yamaları"
```

---

### Task 9: Canlı klip testi

Statik doğrulamanın ulaşamadığı yer: gerçek sayfalar. Bu görev kullanıcının tarayıcısında yürür ve bulguları README'ye yazar.

**Files:**
- Modify: `README.md` (canlı test sonuçları tablosu)
- Modify: `templates/*.json` (bozuk seçiciler düzeltilir)

- [ ] **Step 1: Ayarları içe aktar**

Web Clipper ayarları → Import → `obsidian-web-clipper-settings.json`.
Ardından şablon listesinde 10 şablonu ve **Varsayılan'ın en üstte** olduğunu gözle doğrula.

- [ ] **Step 2: Her şablon için gerçek bir sayfa klipsle**

Her satır için sayfayı aç, eklentinin **doğru şablonu seçtiğini** gör, klipsle.

| Şablon | Test URL'i |
|---|---|
| YouTube | herhangi bir `youtube.com/watch` videosu |
| GitHub | `https://github.com/obsidianmd/obsidian-clipper` |
| Makale | herhangi bir haber/blog yazısı |
| X | herhangi bir tweet permalink'i |
| Reddit | herhangi bir `reddit.com/r/*/comments/*` gönderisi |
| Instagram | herhangi bir `instagram.com/p/*` gönderisi |
| LinkedIn | herhangi bir `linkedin.com/posts/*` gönderisi |
| Ürün | Trendyol veya Amazon ürün sayfası |
| Ekşi Entry | herhangi bir `eksisozluk.com/entry/*` |
| Varsayılan | tetikleyicisiz bir sayfa (örn. bir dokümantasyon sayfası) |

- [ ] **Step 3: Üretilen notları denetle**

Run: `cd "/home/savpavi/Documents/Obsidian/Aktif Kasa/00 Inbox" && ls -1 *.md`
Expected: dosya adları `YYYY-MM-DD -- Kaynak -- Başlık.md` desenine uyar

Run:
```bash
cd "/home/savpavi/Documents/Obsidian/Aktif Kasa/00 Inbox" && grep -l '{{' *.md || echo "Çözülmemiş yer tutucu yok"
```
Expected: `Çözülmemiş yer tutucu yok` — çıkan her dosya, o şablonda bozuk bir değişken olduğunu gösterir

- [ ] **Step 4: `/pulse/` ayrımını doğrula**

Bir `linkedin.com/pulse/` makalesi aç. Eklenti **Makale** şablonunu seçmeli, LinkedIn'i değil.

- [ ] **Step 5: Boş vurgu davranışını test et**

Hiçbir şey işaretlemeden bir makale klipsle. Notun başında boş bir `> [!quote] Vurgular` kutusu kalıyorsa, `makale.json` ve `varsayilan.json` içindeki `noteContentFormat`'tan `|callout:(...)` kısmını çıkarıp yerine düz `{{highlights|map: item => item.content|join:"\n\n"|markdown|blockquote}}` koy ve davranışı README'ye not düş.

- [ ] **Step 6: Şema iç içe erişimini doğrula**

Ürün notunda `price` alanı boşsa, `{{schema:@Product:offers:price}}` yerine `{{schema:@Product:offers.price}}` (nokta) dene ve çalışan biçimi hem şablona hem README'ye işle.

- [ ] **Step 7: Bulguları README'ye yaz**

Her şablon için: çalıştı / kısmen çalıştı (hangi alan boş) / bozuk. Boş kalan alanlar spec'in test kriterine göre kabul edilebilir ama **belgelenmek zorunda** — sessizce geçilmez.

- [ ] **Step 8: Düzeltmeleri derle ve commit et**

```bash
cd "/home/savpavi/Projects/Obsidian Web Clipper"
python3 build.py && python3 -m unittest discover tests -v
git add -A
git commit -m "fix: canlı klip testi bulguları"
```

---

## Öz-denetim notları

**Spec kapsamı:** Spec'teki 10 şablonun her biri bir göreve bağlı (Task 1: Varsayılan; Task 3: Makale + Ekşi; Task 4: YouTube + GitHub; Task 5: X + Reddit; Task 6: Instagram + LinkedIn; Task 7: Ürün). Teslimatlar: `templates/*.json` (Task 1–7), birleşik ayar dosyası (Task 2), `README.md` ve `vault-yamalari.md` (Task 8). Spec'in "canlı klip testiyle doğrulanacaklar" listesindeki dört maddenin dördü de Task 9'da adımlara bağlandı.

**Tip tutarlılığı:** `validate_template(tmpl) -> list[str]` Task 1'de tanımlanıp Task 2'de `build_settings` içinde aynı imzayla çağrılıyor. `templates/_order.json` Task 2'de üretilip Task 3–7'de aynı biçimde (uzantısız slug listesi) genişletiliyor. Şablon dosya adları `_order.json` girdileriyle birebir eşleşiyor.
