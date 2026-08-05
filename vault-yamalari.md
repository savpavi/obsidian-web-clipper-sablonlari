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
`Makale`, `Eksi Entry`, `Klip`

Ornek: `2026-08-05 -- YouTube -- Fedora Kurulum Rehberi.md`

`Klip`, hicbir sablonun tetikleyicisi eslesmediginde devreye giren
Varsayilan sablonun Tip degeridir.
```

---

## Durum

- [ ] Yama 1 `Meta/tag-taxonomy.md`'ye işlendi
- [ ] Yama 2 `Meta/naming-conventions.md`'ye işlendi

Her iki kutu da işaretlenene kadar bu yamalar **uygulanmamış** kabul edilir.
