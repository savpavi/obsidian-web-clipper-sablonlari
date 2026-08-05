# Vault Yamaları — Hazırlanmış, Uygulanmamış

Bu dosya, hedef vault'a (`~/Documents/Obsidian/Aktif Kasa/`) yapılması
gereken iki değişikliği **hazırlar ama uygulamaz**. Bu repo vault'a yazmıyor;
aşağıdaki yamalar kullanıcı onayından sonra ilgili dosyalara elle (veya
onaylı bir sonraki görevde) işlenecek.

Yamalar Web Clipper şablon setinin ürettiği frontmatter/etiketlerin vault'un
kanonik kurallarıyla tutarlı olması için gerekli: yeni `kaynak/*` etiketleri
önce `Meta/tag-taxonomy.md`'de tanımlanmalı ("yeni etiketler önce buraya
eklenmeli" kuralı), ve yeni dosya adı Tip değerleri
`Meta/naming-conventions.md`'deki Tip sözlüğüne eklenmeli.

---

## Yama 1 — `Meta/tag-taxonomy.md`

**Hedef konum:** "LLM Sohbet Kaynaklari" bölümünün hemen ardına.

**Eklenecek metin:**

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

---

## Yama 2 — `Meta/naming-conventions.md`

**Hedef konum:** "Dosyalar" bölümündeki Tip listesinin hemen ardına.

**Eklenecek metin:**

```markdown
**Web Clipper Tip degerleri (2026-08-05):**
`YouTube`, `GitHub`, `X`, `Reddit`, `Instagram`, `LinkedIn`, `Urun`,
`Makale`, `Eksi Entry`, `Eksi Klip`, `Klip`

Ornek: `2026-08-05 -- YouTube -- Fedora Kurulum Rehberi.md`

`Klip`, hicbir sablonun tetikleyicisi eslesmediginde devreye giren
Varsayilan sablonun Tip degeridir. `Eksi Entry` tek bir entry
permalink'ini, `Eksi Klip` ise acik baslik sayfasindaki entry'leri
yakalar; ikisi de `eksi_export.py` scriptinin urettigi tam baslik
arsivlerinden (`type: eksi-baslik`) ayridir.
```

---

## Durum

- [x] Yama 1 `Meta/tag-taxonomy.md`'ye işlendi — 5 Ağustos 2026
- [x] Yama 2 `Meta/naming-conventions.md`'ye işlendi — 5 Ağustos 2026

Her iki yama da kullanıcı onayıyla uygulandı. Uygulama saf ekleme oldu;
mevcut hiçbir satır değişmedi veya silinmedi (`tag-taxonomy.md` 120→130,
`naming-conventions.md` 47→59 satır). `tag-taxonomy.md`'nin frontmatter'ındaki
`last-updated` alanı da `2026-08-05` yapıldı.

Bu dosya artık geçmiş kaydı — yamaların ne olduğunu ve neden gerektiğini
belgeliyor. Tekrar uygulanmasına gerek yok; uygulama betiği zaten
"zaten var, atlandi" diyerek çıkar.
