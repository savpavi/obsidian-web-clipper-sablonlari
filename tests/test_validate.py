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

    def test_yanlis_platform_safe_name_yakalanir(self):
        t = gecerli_sablon()
        t["noteNameFormat"] = '{{date|date:"YYYY-MM-DD"}} -- Deneme -- {{title|safe_name:windows}}'
        self.assertIn("safe_name", " ".join(validate_template(t)))

    def test_notlar_bolumu_yoksa_yakalanir(self):
        t = gecerli_sablon()
        t["noteContentFormat"] = "{{content}}"
        self.assertIn("Notlar", " ".join(validate_template(t)))

    def test_bozuk_regex_tetikleyici_yakalanir(self):
        t = gecerli_sablon()
        t["triggers"] = ["/^https:\\/\\/ornek\\.com\\/(/"]
        self.assertIn("regex", " ".join(validate_template(t)))


if __name__ == "__main__":
    unittest.main()
