# Obsidian Web Clipper Şablon Seti

> **English:** A set of 13 [Obsidian Web Clipper](https://obsidian.md/clipper) templates (YouTube, GitHub, X, Reddit, Instagram, LinkedIn, articles, products, job postings, technical docs, Ekşi Sözlük) with a Python build/validation step and tests. `build.py` compiles `templates/*.json` into one importable settings file; the integration test runs the templates through the official clipper engine. Notes, file names and docs are in Turkish.

13 şablonluk bir set. Tüm şablonlar Obsidian vault'unun `00 Inbox` klasörüne
not düşer; dosya adları `YYYY-MM-DD -- Kaynak -- Başlık` desenini izler.

Her kaynak (YouTube, GitHub, X, Reddit, Instagram, LinkedIn, Ürün, Makale,
Ekşi Entry, Ekşi Klip, İş İlanı, Teknik Dokümantasyon) için ayrı, dar bir şablon var; artı hiçbiri eşleşmezse
devreye giren bir Varsayılan. Siteye özel şablonlar korunur; eksik veriler için `if/set` koşulları kullanılır. Böylece bir site değiştiğinde ilgili şablon bağımsız olarak onarılabilir.

Tasarım gerekçelerinin tamamı için:
`docs/superpowers/specs/2026-08-05-obsidian-web-clipper-sablonlari-design.md`.

## Kurulum

Bu host için **Legacy mode açık** olarak derlenir. 6 Eylül canlı testinde
Brave Origin → Wayland/Obsidian pano aktarımı 0 bayt notlar oluşturdu;
Legacy mode ile Python klibi 2.585 bayt olarak metadata ve gövdesiyle kaydedildi.
Obsidian'a özel geçici odak kuralı sorunu çözmedi ve geri alındı.
Bu sonuç kısa klibin aktarımını doğrular; uzun sayfalarda URI uzunluk sınırı
nedeniyle [dosya olarak kaydetme veya daha kısa klipler](https://obsidian.md/help/web-clipper/troubleshoot)
gerekebilir. Şablonların tüm canlı site testleri tamamlanmış değildir.

**Tüm seti tek seferde kurmak için:**

1. Web Clipper eklentisinde ayarlara git → **Import**.
2. Bu dizindeki `obsidian-web-clipper-settings.json` dosyasını seç.

**Uyarı:** bu dosyayı import etmek Web Clipper'ın **tüm** ayarlarını (vault
listesi, genel ayarlar, highlighter/reader ayarları, mevcut şablonlar) bu
dosyadakiyle değiştirir. Eklentide zaten kurulu başka şablonlar varsa kaybolur.

**Tek bir şablon eklemek için:** `templates/<ad>.json` dosyasını Web
Clipper'ın şablon ekranındaki **Import** düğmesinden tek tek içe aktar. Bu yol
mevcut diğer şablonlara dokunmaz.

`obsidian-web-clipper-settings.json` elle düzenlenmez — `templates/*.json`'dan
`build.py` ile üretilir (bkz. Bakım).

## Şablonlar

Sıra `templates/_order.json`'daki sıradır; bu sıranın Varsayılan'ın neden
başta olduğu "Eşleşme mekaniği" bölümünde açıklanıyor.

| # | Şablon | Tetikleyici | Örnek dosya adı |
|---|---|---|---|
| 1 | Varsayılan | yok (hiçbir şablon eşleşmezse devreye girer) | `2026-08-05 -- Klip -- Baslik Metni` |
| 2 | Ekşi Entry | regex: `eksisozluk.com/entry/<id>` | `2026-09-06 -- Eksi Entry -- Baslik Adi -- 123456` |
| 3 | Ekşi Klip | regex: `eksisozluk.com/<baslik>--<id>` (başlık sayfası) | `2026-08-05 -- Eksi Klip -- Baslik Adi` |
| 4 | YouTube Video | URL öneki: `youtube.com/watch`, `m.youtube.com/watch`, `youtu.be/` | `2026-07-14 -- YouTube -- Video Basligi` |
| 5 | GitHub Repo | regex: `github.com/<kullanici>/<repo>` (alt sayfalar hariç) | `2026-08-05 -- GitHub -- kullanici-repo` |
| 6 | X (Twitter) Post | regex: `x.com` veya `twitter.com` üzerinde `/<handle>/status/<id>` | `2026-09-06 -- X -- kullanici_adi -- 123456` |
| 7 | Reddit Post | regex: `reddit.com/r/<sub>/comments/...` | `2026-08-05 -- Reddit -- Gonderi Basligi` |
| 8 | Instagram Post | regex: `instagram.com/(p\|reel)/...` | `2026-08-05 -- Instagram -- Kullanici Adi` |
| 9 | LinkedIn Gönderi | regex: `linkedin.com/posts/...`, `linkedin.com/feed/update/...` | `2026-08-05 -- LinkedIn -- Ad Soyad` |
| 10 | İş İlanı | LinkedIn `/jobs/view/…` ve schema `@JobPosting` | `2026-09-06 -- Is Ilani -- Support Engineer` |
| 11 | Teknik Dokümantasyon | Belirli dokümantasyon alan adları, GitHub issue/PR permalinkleri, `@TechArticle` / `@APIReference` | `2026-09-06 -- Teknik -- Kurulum` |
| 12 | Ürün | schema: `@Product` | `2026-08-05 -- Urun -- Urun Adi` |
| 13 | Makale | schema: `@Article`, `@NewsArticle`, `@BlogPosting` | `2026-06-12 -- Makale -- Yazi Basligi` |

Tüm şablonlarda ortak: `path: "00 Inbox"`, `behavior: "create"`,
`type: referans` frontmatter alanı, `source`/`source_type` alanları, ve
gövdenin sonunda kullanıcının dolduracağı boş bir `## Notlar` bölümü.

## Eşleşme mekaniği

Web Clipper hangi şablonu kullanacağına şu sırayla karar veriyor
(`obsidianmd/obsidian-clipper` kaynağından doğrulandı, tahmin değil):

1. **URL öneki** — bir trie üzerinde en uzun eşleşme kazanır. Bu sette
   yalnızca YouTube'un tetikleyicileri bu türde.
2. **Regex** — `/^https:\/\/.../` biçimindeki tetikleyiciler. Ekşi Entry,
   GitHub, X, Reddit, Instagram, LinkedIn ile yeni ilan/dokümantasyon URL
   kuralları bu türde.
3. **Şema** — `schema:@Product`, `schema:@Article` gibi tetikleyiciler.
   **Yalnızca ilk iki kademe de başarısız olursa** denenir. Ürün ve Makale
   bu türde; İş İlanı ve Teknik Dokümantasyon da şema tetikleyicileri taşır.

Kaynak: `src/utils/triggers.ts`.

**Kritik nokta:** hangi kademenin öne çıkacağını **liste sırası değil,
tetikleyici türü** belirliyor. Bu yüzden:

- LinkedIn'in regex tetikleyicisi, Makale'nin `@Article` şemasını **her zaman**
  yener — `templates/_order.json`'da Makale'nin LinkedIn'den sonra gelmesinin
  bir önemi yok, `linkedin.com/pulse/...` (`@Article` şeması taşıdığında)
  yine de LinkedIn'e değil Makale'ye düşer çünkü LinkedIn'in regex'i
  `/posts/` ve `/feed/update/` yollarıyla sınırlı, `/pulse/` onu eşlemez.
- Liste sırası yalnızca **aynı kademedeki** şablonlar arasında karar veriyor.
  Şema kademesinde İş İlanı ve Teknik Dokümantasyon, Ürün ve Makale
  öncesinde değerlendirilir. Bir sayfa hem `JobPosting` hem `Article` taşıyorsa
  İş İlanı seçilir; `TechArticle` Teknik Dokümantasyon tarafından karşılanır.

**Hiçbir tetikleyici eşleşmezse** `findMatchingTemplate` `undefined`
döndürür ve `src/core/popup.ts` içindeki fallback devreye girer:
`currentTemplate = templates[0]` — yani **listedeki ilk şablon**, liste
konumundan bağımsız bir "en son çare" değil, gerçekten dizinin sıfırıncı
elemanı. Bu yüzden `_order.json`'da Varsayılan ilk sırada: eşleşmeyen bir
sayfa Varsayılan'a değil de örneğin Ekşi Entry'ye düşmesin diye.

## 6 Eylül 2026 güncellemesi

- **İş İlanı:** `company`, `location`, `employment_type`, `workplace_type`,
  `salary`, `deadline`. Alanlar yalnız sayfanın `JobPosting` verisinden alınır;
  şema yoksa boş kalır. Maaşın net/brüt niteliği veya hibrit çalışma modeli
  tahmin edilmez. Maaşta `baseSalary.value.value` veya `minValue/maxValue`,
  para birimi ve dönem desteklenir. Konum şehir/ülke alanlarından gelir.
  Gövde seçili metin → şema açıklaması → genel içerik sırasını izler.
  Kaydetmek, başvuru yapıldığı anlamına gelmez.
- **Teknik Dokümantasyon:** Kod bloklu içerik ve kullanıcı tarafından doldurulan
  amaç, ortam/sürüm, doğrulama bölümleri. `help.obsidian.md`, `obsidian.md/help/`,
  `docs.python.org`, `developer.mozilla.org`, `wiki.archlinux.org` ile GitHub
  `/issues/<id>` ve `/pull/<id>` adresleri otomatik eşleşir. Diğer teknik
  sayfalarda şablon elle seçilebilir; `TechArticle`/`APIReference` şeması da tetikler.
- **Eksik başlık/tarih:** Başlık için genel sayfa başlığı, o da yoksa “Başlıksız”
  kullanılır. Yayım tarihi bulunamazsa `date` yakalama tarihine döner;
  `created` her zaman yakalama tarihidir.
- **Dosya adları:** X'e gönderi kimliği, Ekşi Entry'ye entry kimliği eklendi.
  Aynı tarih/yazar veya başlıktaki farklı içerikler ayrılır. Önceki notlar
  yeniden adlandırılmaz; eski klibi tekrar kaydetmek yeni adla ikinci not oluşturabilir.
- **GitHub:** Query/fragment içeren repo adresleri eşleşir; takip parametreleri
  dosya adına ve `repo` alanına taşınmaz. `source` özgün URL'yi korur.
- **LinkedIn/Instagram:** Seçili metin → `og:description` → açık “metin alınamadı”
  mesajı. LinkedIn'in bütün feed'i gövdeye alınmaz. Oturum duvarını aşmaz;
  sayfada görünür gönderi metnini seçmek önerilir.
- **Boş bölümler:** Reddit'te yorum yoksa İlk Yorum bölümü, Ürün'de fiyat/puan
  yoksa ilgili satırlar gösterilmez. Ürün puanına varsayımsal `/5` eklenmez.

### Motor uyumluluğu ve doğrulama

[Resmî Logic belgesi](https://obsidian.md/help/web-clipper/logic) koşullu mantığı
belgeliyor. Bu sette `if/set` kullanılır. Belgelenen `??` kısayolu test edilen
Knap 0.2.3 motorunda derleme hatası verdiği için kullanılmadı.

6 Eylül'de Web Clipper kaynak sürümü **1.7.1**, commit
`a9d33ce919fb156beda390d2fc60cbc1e0ed9141` ile **28 entegrasyon testi** geçti.
Testler resmî compiler, filtreler ve tarayıcı tetikleyici motorunu kullanır;
kontrollü sayfa verileri, DOM seçicileri ve bir HTML/JSON-LD ilan örneği içerir.
Bunlar oturum açılmış canlı LinkedIn/Instagram sayfası testi değildir.
Bu motor testi sırasında kurulu tarayıcı eklentisi ve import sonrası görünüm
doğrulanmamıştı. Sonraki canlı Legacy mode sonucu için Kurulum bölümüne bakın.

Python kontrolleri (24 test):

```bash
python3 build.py
python3 -m unittest discover tests
```

Motor testini yeniden çalıştırmak için resmî depoyu ayrı bir geçici klasöre
klonlayın; proje kökünden aşağıdaki komutları kullanın (Node.js/npm gerekir).
Bağımlılıklar yalnız geçici checkout'a kurulur. O commit'in kilit dosyası
`npm ci` ile iki eksik bağımlılık hatası verdiğinden `npm install` kullanılmıştır.

```bash
clipper_test_dir="$(mktemp -d /tmp/clipper-test.XXXXXX)"
git clone https://github.com/obsidianmd/obsidian-clipper.git "$clipper_test_dir"
git -C "$clipper_test_dir" checkout a9d33ce919fb156beda390d2fc60cbc1e0ed9141
npm --prefix "$clipper_test_dir" install --ignore-scripts --no-audit --no-fund
cp tests/clipper.integration.test.ts "$clipper_test_dir/src/utils/local-templates.test.ts"
CLIPPER_TEMPLATE_ROOT="$PWD" "$clipper_test_dir/node_modules/.bin/vitest" \
  run --root "$clipper_test_dir" src/utils/local-templates.test.ts
```

`tests/test_build.py` kaydedilen import dosyasının güncelliğini de denetler.
Şablonu değiştirip derlemeyi unutmak test hatası verir.

## `{{highlights}}` ve `{{content}}` üzerine notlar

**Şablonlarda ayrı bir vurgu bölümü yok — bilerek.** Vurgular zaten
`{{content}}` içinde geliyor.

Tasarımda "üstte vurgular, altta tam metin" düzeni planlanmıştı ve Makale ile
Varsayılan şablonlarına şöyle bir blok konmuştu:

```
{{highlights|map: item => item.content|blockquote}}
```

Canlı testte (5 Ağustos 2026) bunun iki sorunu çıktı:

1. **Vurgusuz her klipte tek başına bir `> ` satırı kalıyordu.** Sebep
   yapısal: `map` filtresi JSON olarak ayrıştıramadığı girdiyi `[""]` diye
   tek elemanlı bir diziye sarıyor (`src/utils/filters/map.ts`, catch
   bloğu), `blockquote` da o boş elemanı `> ` olarak basıyor. Filtre
   zinciriyle kaçınmanın yolu yok.
2. **Blok zaten gereksizdi.** Highlighter bu sette `highlight-inline`
   modunda (bkz. `obsidian-web-clipper-settings.json` →
   `highlighter_settings`), ve vurgular `{{content}}` içine Obsidian'ın
   kendi `==vurgu==` sözdizimiyle gömülü halde geliyor. Bu, vurgu bloğu
   **bulunmayan** bir LinkedIn klibinde işaretlenen metnin `==` ile sarılmış
   çıkmasıyla doğrulandı.

Yani blok, aynı metni ikinci kez yazıp karşılığında her nota bir artık satır
bırakıyordu. Kaldırıldı. Vurguların kendisi kaybolmadı — gövdede `==` ile
işaretli duruyor, Obsidian sarı zeminle render ediyor ve arama/Dataview
görüyor.

Değişkenin yapısı hakkında, ileride gerekirse: `{{highlights}}` bir dizi
döndürür ve her elemanın metni **`text` değil `content` anahtarında**, HTML
biçiminde durur.

## Kırılganlık haritası — 5 Ağustos tarihsel sürümü

Her şablonun neye bağlı olduğu, o şablonun `noteContentFormat` ve
`properties` alanlarından okunuyor — aşağıdaki tablo tahmini değil, gerçek
dosyalardan çıkarıldı.

| Şablon | Bağımlılık | Bozulursa |
|---|---|---|
| Varsayılan | Genel sayfa çıkarımı: `{{title}}`, `{{author}}`, `{{site}}`, `{{description}}`, `{{content}}` | En dayanıklı şablon; sayfa çok atipikse tek tek alanlar boş gelebilir, tamamen boşalmaz |
| Ekşi Entry | DOM seçicileri: `a.entry-author`, `#entry-item-list li div.content` | Ekşi Sözlük arayüzü class/id değiştirirse yazar ve entry metni boş kalır |
| Ekşi Klip | DOM seçicileri: `#entry-item-list li div.content` (entry metinleri), `#entry-item-list li a.entry-author` (yazarlar) | Aynı risk; ayrıca yalnızca **açık sayfadaki** entry'leri yakalar — başlığın tamamı için `eksi_export.py` script'i kullanılmalı |
| YouTube Video | schema.org `@VideoObject` (`name`, `uploadDate`, `description`, `author`, `duration`) | YouTube şemayı kaldırır/değiştirirse tüm alanlar birden boş kalır |
| GitHub Repo | `og:description` meta + DOM seçici `#repo-stars-counter-star`; gövde `{{content}}` üzerinden README'nin tamamı | Yıldız sayacının id'si değişirse yalnızca `stars` boş kalır, gerisi çalışmaya devam eder |
| X (Twitter) Post | DOM seçicisi `div[data-testid="tweetText"]` (gövde ve `title`) + URL'den handle çıkarma | X bu testid'yi değiştirirse tweet metni boş kalır; handle URL'den geldiği için her hâlükârda durur. **Not:** ilk sürüm metni sayfa başlığından ayrıştırıyordu, X başlık biçimini değiştirdiği için 5 Ağustos 2026'da DOM'a taşındı |
| Reddit Post | `shreddit-*` özel web component'lerinin attribute seçicileri (`post-title`, `author`, `score`, `created-timestamp`, yorum gövdesi) | Reddit bu bileşenleri değiştirirse şablon büyük ölçüde boşalır — bu sette en kırılgan seçici seti |
| Instagram Post | `og:title` / `og:description` meta etiketleri | Login duvarı arkasında bu meta etiketler boş veya jenerik gelebilir; bu sette en kırılgan şablon |
| LinkedIn Gönderi | `og:title` / `og:description` meta etiketleri; gövde `{{content}}` | Login duvarı arkasında boş gelebilir |
| Ürün | schema.org `@Product` (`name`, `image`, `offers.price`, `offers.priceCurrency`, `brand.name`, `offers.availability`, `aggregateRating`) | Mağaza şemayı kaldırır/değiştirirse fiyat-puan tablosu boş kalır; şema tabanlı olduğu için Amazon, Trendyol, Hepsiburada dahil şema yayınlayan her mağazada aynı şekilde çalışır |
| Makale | schema.org tetikleyicisi (`@Article`/`@NewsArticle`/`@BlogPosting`/`@TechArticle`) yalnızca eşleşme için; gövde genel sayfa çıkarımına (`{{content}}`, `{{highlights}}`) dayanır | Nadiren bozulur — hem şema tetikleyicisinin hem genel içerik çıkarımının aynı anda başarısız olması gerekir |

## Bakım

Bir şablonu değiştirmek gerektiğinde (bir site HTML'ini değiştirdi, yeni bir
alan eklenecek, vb.):

1. İlgili `templates/<ad>.json` dosyasını düzenle.
2. `python3 build.py` çalıştır — `obsidian-web-clipper-settings.json`'ı
   yeniden üretir. Bu adım `validate.py`'deki vault kurallarını da
   uygular; kural ihlali varsa `build.py` hata verip durur.
3. `python3 -m unittest discover tests` çalıştır — tüm testler yeşil olmalı.
4. Değişen şablonu (ya tekini `templates/<ad>.json` üzerinden ya da tüm
   seti `obsidian-web-clipper-settings.json` üzerinden) Web Clipper'a
   yeniden import et.

`obsidian-web-clipper-settings.json` **elle düzenlenmez** — `templates/*.json`
tek doğruluk kaynağı, bu dosya yalnızca üretilen çıktıdır. Elle yapılan
değişiklikler bir sonraki `python3 build.py` çalıştırmasında sessizce
kaybolur.

Toplu çıktıdaki şablon kimlikleri (`id`) slug'dan deterministik üretiliyor
(`_id_uret` fonksiyonu, `build.py`). Tekil importta eklentinin sürümüne göre
kopya oluşabilir; importtan sonra şablon listesini kontrol edin.

Yeni bir şablon eklerken (mevcut bir dosyayı düzenlemek değil, `templates/`
altına yeni bir `<ad>.json` koymak):

1. Yukarıdaki adımlara ek olarak, yeni dosyayı `templates/_order.json`
   dizisine de ekle. `build.py` bu listeyi kullanıyor, dizini glob'lamıyor —
   listeye eklenmeyen bir şablon dosyası derlemeye sessizce girmez, `build.py`
   yine "10 şablon derlendi" gibi başarı mesajı basar ve boşluk fark edilmez.
2. Listedeki konumunu **kademesine göre** seç: önce URL öneki tetikleyicili
   şablonlar, sonra regex tetikleyicililer, en sonda şema tetikleyicililer
   ("Eşleşme mekaniği" bölümüne bakın). Liste sırası yalnızca **aynı
   kademedeki** şablonlar arasında karar veriyor — farklı kademeler arasında
   sıranın hiçbir etkisi yok.

## Canlı test sonuçları — 5 Ağustos tarihsel sürümü

İlk canlı tur **5 Ağustos 2026**'da gerçek sayfalar klipslenerek yapıldı.
Sonuçlar üretilen notlar okunarak çıkarıldı, beyana dayanmıyor.

| Şablon | Durum | Bulgu |
|---|---|---|
| Reddit Post | ✅ | `title`, `subreddit`, `author`, `score`, gövde metni tam geldi. `shreddit-*` seçicileri geçerli. |
| Makale | ✅ | Sorun yok. |
| GitHub Repo | ⚠️ | `title` doğru (`kullanici/repo`), `description` ve gövde tam. **`stars` boş** — `#repo-stars-counter-star` istemci tarafında render ediliyor. |
| Ürün | 🔧 düzeltildi | `price`, `currency`, `brand`, `rating`, `availability` boş geldi: iç içe şema erişimi **iki nokta değil nokta** istiyormuş (`offers.price`). `image` de ham `ImageObject` döküyordu → `image.contentUrl\|first`. Trendyol'un JSON-LD'si doğrudan incelenerek doğrulandı. |
| X (Twitter) Post | 🔧 düzeltildi | Tweet metni gelmiyordu: X sayfa başlığına artık metni koymuyor, yalnızca `Post by @kullanici on X` yazıyor, bu yüzden `" on X: "` ayrıştırması gövdeye kırpılmış çöp bırakıyordu. Metin artık DOM'dan alınıyor (`div[data-testid="tweetText"]`). |
| Varsayılan | 🔧 düzeltildi | Çalışıyordu, ama vurgu yapılmadan klipslenince boş "Vurgular" kutusu bırakıyordu. Zincir düzeltildi (yukarıdaki bölüm). |
| Ekşi Entry | ⏳ | Doğrudan denenmedi — klipslenen URL başlık sayfasıydı, bu yüzden **Ekşi Klip** şablonu eklendi. Permalink testi bekliyor. |
| Instagram Post | ❌ | `title`, `author`, `image` **hepsi boş**. `og:` etiketleri login duvarı arkasında veri döndürmüyor. DOM'a inmeden çözümü yok; bilinçli olarak bu haliyle bırakıldı. |
| YouTube Video | ⏳ | Bu turda denenmedi. |
| LinkedIn Gönderi | ⏳ | Bu turda bir gönderi permalink'i denenmedi (yalnızca iş ilanı sayfası klipslendi, o da doğru şekilde Varsayılan'a düştü). |
| Ekşi Klip | ⏳ | Bu turdan sonra eklendi, henüz denenmedi. |

### İkinci tur (aynı gün, düzeltmelerden sonra)

| Şablon | Durum | Bulgu |
|---|---|---|
| Ürün | ✅ | `price: 199.9`, `currency: TRY`, `brand`, `rating: 4`, `availability: InStock`, `image` gerçek URL. Detay tablosu tam doldu. Nokta gösterimi doğrulandı. |
| X (Twitter) Post | ✅ | `title` artık tweet metni, gövdede metin var. Emoji `![🚨](...svg)` olarak geliyor — sadakatli ama biraz gürültülü. |
| YouTube Video | ✅ | `title`, `channel`, `duration: 00:27:34` (`\|duration` filtresi çalışıyor), yayın tarihi dosya adında doğru, açıklama tam. |
| Ekşi Klip | 🔧 düzeltildi | Tetikleyici ve frontmatter doğru, ama `#entry-item-list` her entry'nin paylaş/şikayet/modlog menüsünü de çekiyordu. Seçici `#entry-item-list li div.content` olarak daraltıldı, yazarlar ayrı alana alındı. |
| LinkedIn Gönderi | ❌ | Instagram'la aynı: `title`, `author`, `description` boş, gövde ham feed iskeleti ve reklam takip URL'leri. `og:` etiketleri login duvarı arkasında veri taşımıyor. |
| Boş vurgu | 🔧 çözüldü | Vurgu bloğu Makale ve Varsayılan'dan kaldırıldı. Üçüncü tur doğrulaması: vurgu bloğu **bulunmayan** bir LinkedIn klibinde işaretlenen metin `==` ile sarılmış geldi, yani vurgular zaten `{{content}}` içinde taşınıyor ve ayrı blok sadece tekrar + artık satır üretiyormuş. |

### Üçüncü tur (vurgu doğrulaması)

Bir sayfada metin işaretlenip klipslendi. Sonuç: vurgu `{{content}}` içinde
Obsidian'ın `==vurgu==` sözdizimiyle geldi. Bu, "üstte vurgular, altta tam
metin" tasarım kararını geçersiz kıldı — bilgi zaten gövdede olduğu için üstteki
blok kaldırıldı, `> ` artığı da onunla birlikte gitti.

### Dördüncü tur (kalan üç şablon)

| Şablon | Durum | Bulgu |
|---|---|---|
| Ekşi Entry | ✅ | `author: msb`, `entry_id`, `baslik`, `moc` dolu; entry metni alıntı bloğu olarak temiz geldi. |
| Ekşi Klip | ✅ | Daraltılmış seçici tuttu — paylaş/şikayet/modlog menüleri gitti, sayfadaki 10 entry ve 10 yazar doğru geldi. |
| Reddit Post | ✅ | Daha önce denenmemiş **"İlk Yorum"** bölümü de dahil hepsi çalışıyor. |
| Boş vurgu | ✅ | Yeni notların hiçbirinde `> ` artığı yok. Kalan 6 örnek düzeltme öncesi klipler. |

Bu turda çıkan tek kusur: Ekşi Klip'te entry'ler arasına koyduğum `---`
ayırıcı, `markdown` filtresi tarafından `\---` diye kaçırılıyordu (turndown
`---`'ı olası yatay çizgi/başlık altı çizgisi sayıp escape ediyor), yani
yatay çizgi yerine düz metin görünüyordu. Ayırıcı `···` yapıldı.

**5 Ağustos şablon setinin durumu:** Instagram ve LinkedIn dışında hepsi doğrulandı.
O ikisi login duvarı arkasında `og:` etiketleri veri döndürmediği için
boş kalıyor; DOM seçicilerine inmeden çözümü yok, bilinçli olarak bu halde
bırakıldı. GitHub'ın `stars` alanı da istemci tarafında render edildiği
için boş — şablonun geri kalanı çalışıyor.

Test kriteri (bkz. tasarım dokümanı, "Test kriteri" bölümü): dosya adı
`YYYY-MM-DD -- {{Kaynak}} -- {{Başlık}}` desenine uyuyor mu, frontmatter
zorunlu alanları ve doğru `kaynak/*` etiketini taşıyor mu, gövdede boş kalan
`{{...}}` yer tutucusu var mı. Kırılgan üçlü (Instagram, LinkedIn, X) için
2. ve 3. koşulun kısmen sağlanması beklenebilir; bu durumda hangi alanın boş
kaldığı bu tabloya not düşülecek.
