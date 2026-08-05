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
