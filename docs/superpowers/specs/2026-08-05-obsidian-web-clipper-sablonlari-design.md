# Obsidian Web Clipper Şablon Seti — Tasarım

**Tarih:** 2026-08-05
**Durum:** Onaylandı, uygulamaya hazır
**Hedef vault:** `~/Documents/Obsidian/Aktif Kasa/`

## Amaç

Obsidian Web Clipper tarayıcı eklentisi için, hedef vault'un kanonik kurallarına
(`Meta/naming-conventions.md`, `Meta/tag-taxonomy.md`, `Meta/vault-structure.md`)
uyan 10 şablonluk bir set üretmek.

Mevcut durum: `~/Desktop/Ege/Programlar/obsidian-web-clipper-settings.json`
(19 Mart 2026) içinde 7 şablon var, ancak eklentide kurulu değiller ve vault
kurallarıyla üç noktada çakışıyorlar:

| Vault kuralı | Eski şablonlardaki durum |
|---|---|
| Dosya adı `YYYY-MM-DD -- {{Tip}} -- {{Başlık}}` | ` -- ` ayırıcısı yok (`2026-03-19 YT Başlık`) |
| İngilizce sistem-tag yasak; `#article`/`#clipping`/`#video` → `#kaynak` | `tags: clipping, youtube` |
| Klip şablonları `type: referans` taşımalı | `type` alanı hiç yok |

Bu dosya sıfırdan kurulan yeni seti tanımlar. Eski dosya yalnızca fikir kaynağıdır.

## Kapsam dışı

- Interpreter (LLM) tabanlı özetleme — eklentide kapalı, API anahtarı yok.
  Tüm şablonlar deterministik kalır.
- `03-Resources/Eksi/` altındaki `eksi_export.py` script'i — dokunulmuyor.
- Klip sonrası yönlendirme/triage otomasyonu — mevcut inbox akışına bırakılıyor.

## Kararlar

Tasarım sırasında alınan ve gerekçesi kayda değer kararlar:

1. **Kaynak başına bir şablon.** Web Clipper'da koşullu mantık yok. Tek "akıllı"
   şablon yerine 10 dar şablon; maliyeti sayı, kazancı bir site HTML'ini
   değiştirdiğinde yalnızca o şablonun tamir edilmesi.
2. **Hepsi `00 Inbox`'a yazar.** Tip başına doğrudan hedef klasör yerine tek kapı;
   dağıtımı mevcut inbox-triage akışı yapar.
3. **Dosya adındaki `{{Tip}}` alanı kaynak adıdır** (`YouTube`, `GitHub`, `X`…),
   sabit `Referans` değil. Dosya listesinde kaynağın anında görünmesi için.
   Bu, `naming-conventions.md`'deki Tip sözlüğünü 10 yeni değerle genişletir.
4. **Tarih önceliği: yayın tarihi > klip tarihi.** Kronolojik sıralamanın anlamlı
   olması için. Yayın tarihi vermeyen kaynaklarda (GitHub, Ürün) klip tarihi.
5. **Makale gövdesi: vurgular üstte, tam metin altta.** Arşiv değeri korunur,
   aranan yer hızlı bulunur.
6. **Ekşi şablonu tek entry yakalar, başlık sayfası değil.** Gerekçe aşağıda.

### Ekşi çakışması ve çözümü

`03-Resources/Eksi/` altındaki notlar `eksi_export.py` tarafından üretiliyor ve
bir başlığın **tamamını** içeriyor (örn. 721 entry / 73 sayfa). Kendi frontmatter
sözleşmeleri var: `type: eksi-baslik`, `topic_id`, `sayfa_sayisi`, `entry_sayisi`,
`moc: "[[Eksi Kaynaklari MOC]]"`.

Web Clipper yalnızca tarayıcıdaki tek sayfayı görebilir. Aynı `type` ve isim
desenini kullansaydı, 20 entry'lik kısmi bir klip ile 721 entry'lik tam arşiv
aynı Dataview sorgusuna düşerdi.

**Çözüm:** Ekşi şablonu `eksisozluk.com/entry/<id>` permalink'lerini hedefler —
yani tek bir entry. `type: referans`, `source_type: eksi-entry`. Farklı bir iş
görür, script arşivleriyle hiçbir noktada çakışmaz.

## Ortak omurga

Her şablon aynı iskeleti paylaşır.

### Dosya adı

```
{{tarih|date:"YYYY-MM-DD"}} -- {{Kaynak}} -- {{başlık|safe_name|slice:0,60}}
```

`{{tarih}}` = yayın tarihi; kaynak vermiyorsa klip tarihi.
`{{Kaynak}}` = sabit metin, şablona özel (`YouTube`, `GitHub`, `Reddit`…).

### Frontmatter — ortak alanlar

```yaml
type: referans          # vault Tip sözlüğü, tüm klip şablonlarında sabit
date: 2026-08-05        # yayın tarihi (yoksa klip tarihi)
created: 2026-08-05     # klip anı, her zaman
tags: [kaynak, kaynak/<kaynak>]
source: https://...     # orijinal URL, her zaman
source_type: youtube    # makine-okunur tip, Dataview/Bases için
title: ...
author: ...             # kaynak veriyorsa
```

Kaynağa özel alanlar buna eklenir (`channel`, `duration`, `subreddit`, `price`,
`stars`, `entry_id`…).

### Etiketler

Mevcut `#kaynak/claude`, `#kaynak/chatgpt`, `#kaynak/gemini` deseni uzatılır:

```
kaynak/youtube   kaynak/github   kaynak/makale   kaynak/x       kaynak/instagram
kaynak/reddit    kaynak/urun     kaynak/linkedin kaynak/eksi
```

İngilizce düz tag (`clipping`, `article`, `video`) kullanılmaz — taksonomi
açıkça yasaklıyor.

**Bu işin parçası:** `Meta/tag-taxonomy.md`'ye 9 yeni `kaynak/*` etiketi
eklenecek ("yeni etiketler önce buraya eklenmeli" kuralı gereği).

### Gövde düzeni

Üç blok, her şablonda aynı sırada:

1. Kaynağa özel üstbilgi — gömülü video/tweet, meta tablosu, alıntı satırı
2. İçerik — tam metin, açıklama veya gönderi gövdesi
3. `## Notlar` — kullanıcının yazacağı boş alan

### Hedef klasör

Tümü `00 Inbox`.

## Şablonlar

Sıralama kritik: Web Clipper listedeki **ilk eşleşen** şablonu kullanır.
Dar regex'ler üstte, geniş şema tetikleyicileri altta, yakalanmayan her şey
Varsayılan'a.

### 1. Ekşi Entry

- **Tetikleyici:** regex `eksisozluk.com/entry/\d+`
- **Ad:** `2026-08-05 -- Eksi Entry -- baslik`
- **Alanlar:** `baslik` (entry'nin bağlı olduğu başlık), `yazar`, `entry_id`,
  `source_type: eksi-entry`, `moc: "[[Eksi Kaynaklari MOC]]"`
- **Etiketler:** `kaynak`, `kaynak/eksi`, `eksi`
- **Gövde:** entry metni alıntı bloğu olarak → `## Notlar`
- **Not:** `type: eksi-baslik` **kullanılmaz** — script arşivlerinden ayrışması için

### 2. YouTube Video

- **Tetikleyici:** `https://www.youtube.com/watch`, `https://youtu.be/`
- **Ad:** `2026-07-14 -- YouTube -- Baslik`
- **Alanlar:** `channel`, `duration`, `published` (schema `@VideoObject`)
- **Etiketler:** `kaynak`, `kaynak/youtube`
- **Gövde:** gömülü oynatıcı → açıklama (2000 karakter kırpma) → `## Notlar`

### 3. GitHub Repo

- **Tetikleyici:** regex `^https://github\.com/[\w-]+/[\w.-]+$` (alt sayfalar hariç)
- **Ad:** `2026-08-05 -- GitHub -- kullanici-repo`
- **Alanlar:** `repo` (`kullanici/repo`), `language`, `stars`, `description`
- **Etiketler:** `kaynak`, `kaynak/github`, `alan/teknik`
- **Gövde:** README tamamı (`{{content}}`) → `## Notlar`
- **Not:** Başlıktaki ` · GitHub` eki temizlenir

### 4. X (Twitter) Post

- **Tetikleyici:** regex `x.com` ve `twitter.com` için `/<handle>/status/<id>`
- **Ad:** `2026-08-05 -- X -- @handle`
- **Alanlar:** `author`, `handle`, `published`
- **Etiketler:** `kaynak`, `kaynak/x`
- **Gövde:** gömülü tweet → tweet metni (sayfa başlığından ayrıştırılır) →
  varsa görsel → `## Notlar`
- **Kırılganlık:** login duvarı + DOM bağımlı

### 5. Reddit Post

- **Tetikleyici:** regex `reddit\.com/r/\w+/comments`
- **Ad:** `2026-08-05 -- Reddit -- r-subreddit -- Baslik`
- **Alanlar:** `subreddit`, `author` (`u/...`), `score`, `published`
- **Etiketler:** `kaynak`, `kaynak/reddit`
- **Gövde:** alıntı satırı (sub · yazar · oy) → gönderi gövdesi → varsa görsel →
  en üstteki yorum → `## Notlar`
- **Kırılganlık:** `shreddit-*` web component seçicilerine bağlı

### 6. Instagram Post

- **Tetikleyici:** regex `instagram\.com/(p|reel)/`
- **Ad:** `2026-08-05 -- Instagram -- @kullanici`
- **Alanlar:** `author`, `published`
- **Etiketler:** `kaynak`, `kaynak/instagram`
- **Gövde:** kapak görseli → `og:description`'dan caption → `## Notlar`
- **Kırılganlık:** Bu setin en kırılgan halkası. Login duvarı arkasında ve class
  isimleri sürekli değişiyor. Veri `og:` meta etiketlerinden çekilir (görece
  stabil), ancak YouTube/Reddit kadar zengin sonuç beklenmemeli.

### 7. LinkedIn Gönderi

- **Tetikleyici:** regex `linkedin\.com/posts/`, `linkedin\.com/feed/update/`
- **Ad:** `2026-08-05 -- LinkedIn -- Ad Soyad`
- **Alanlar:** `author`, `author_title` (kişinin başlık satırı), `published`
- **Etiketler:** `kaynak`, `kaynak/linkedin`
- **Gövde:** gönderi metni → varsa görsel → `## Notlar`
- **Not:** `linkedin.com/pulse/` bu şablona **girmez**. O sayfalar `@Article`
  şeması taşıdığı için Makale şablonuna düşer ve tam metin + vurgu muamelesi
  görür — istenen davranış budur.
- **Kırılganlık:** login duvarı + DOM bağımlı

### 8. Ürün

- **Tetikleyici:** `schema:@Product`
- **Ad:** `2026-08-05 -- Urun -- Urun Adi`
- **Alanlar:** `price`, `currency`, `store`, `brand`, `rating`, `availability`,
  `image`
- **Etiketler:** `kaynak`, `kaynak/urun`
- **Gövde:** ürün görseli → fiyat/mağaza/stok/puan tablosu → açıklama → `## Notlar`
- **Not:** Şema tabanlı olduğu için Amazon, Trendyol, Hepsiburada dahil şema
  yayınlayan her mağazada çalışır

### 9. Makale

- **Tetikleyici:** `schema:@Article`, `@NewsArticle`, `@BlogPosting`, `@TechArticle`
- **Ad:** `2026-06-12 -- Makale -- Baslik`
- **Alanlar:** `author`, `site`, `description`, `published`
- **Etiketler:** `kaynak`, `kaynak/makale`
- **Gövde:** `## Vurgular` (kullanıcının işaretledikleri) → `---` → tam metin →
  `## Notlar`

### 10. Varsayılan

- **Tetikleyici:** yok — hiçbiri eşleşmezse devreye girer
- **Ad:** `2026-08-05 -- Klip -- Baslik`
- **Etiketler:** `kaynak`
- **Gövde:** vurgular → tam metin → `## Notlar`

## Teslimatlar

`/home/savpavi/Projects/Obsidian Web Clipper/` altında:

| Dosya | İçerik |
|---|---|
| `templates/*.json` | Her şablon ayrı dosya; eklentiye tek tek "Import" edilebilir |
| `obsidian-web-clipper-settings.json` | Hepsi birleşik; tek seferde içe aktarım |
| `README.md` | Kurulum adımları + bir site HTML'ini değiştirdiğinde tamir rehberi |
| `vault-yamalari.md` | `Meta/tag-taxonomy.md` için 9 yeni `kaynak/*` etiketi **ve** `Meta/naming-conventions.md` için genişleyen Tip sözlüğü (Karar 3) |

Vault dosyalarına yama **doğrudan uygulanmaz** — hazırlanır, kullanıcı onayından
sonra işlenir.

## Uygulama öncesi doğrulanacaklar

Hafızadan yazılmayacak, resmî Obsidian Web Clipper dokümanına bakılarak teyit
edilecek noktalar:

1. **`{{highlights}}` değişkeninin tam sözdizimi** — dizi mi döndürüyor, hangi
   filtre ile (`|map`, `|template`, `|blockquote`) markdown'a çevriliyor.
   Makale ve Varsayılan şablonlarını doğrudan etkiler.
2. **Reddit `shreddit-*` seçicileri** — `shreddit-post?post-title`,
   `?subreddit-prefixed-name`, `?author`, `?score`, `?created-timestamp` ve
   yorum ağacı seçicisi hâlâ geçerli mi.
3. **Instagram ve LinkedIn seçicileri** — hangi `og:` alanları ve DOM
   seçicileri gerçekten veri döndürüyor.
4. **Şablon JSON şeması** — `schemaVersion`, `id` üretimi, `template_list`
   sıralaması ve `property_types` kaydının içe aktarımda beklenen biçimi.

## Test kriteri

Her şablon için: gerçek bir URL klipslenir, üretilen not şu üç koşulu sağlamalı.

1. Dosya adı `YYYY-MM-DD -- {{Kaynak}} -- {{Başlık}}` desenine uyuyor
2. Frontmatter `type: referans` (Ekşi dahil), `source`, `source_type`, `created`
   ve doğru `kaynak/*` etiketini taşıyor; hiçbir İngilizce düz sistem-tag yok
3. Gövdede boş kalan `{{...}}` yer tutucusu yok

Kırılgan üçlü (Instagram, LinkedIn, X) için 2. ve 3. koşul kısmen sağlanabilir;
bu durumda hangi alanın boş kaldığı `README.md`'ye not düşülür.
