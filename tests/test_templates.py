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
