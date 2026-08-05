# Obsidian Web Clipper Şablon Seti

11 şablonluk bir set. Hedef vault `~/Documents/Obsidian/Aktif Kasa/`; tüm
şablonlar `00 Inbox` klasörüne not düşer, dağıtımı mevcut inbox-triage akışı
yapar.

Her kaynak (YouTube, GitHub, X, Reddit, Instagram, LinkedIn, Ürün, Makale,
Ekşi Entry, Ekşi Klip) için ayrı, dar bir şablon var; artı hiçbiri eşleşmezse
devreye giren bir Varsayılan. Web Clipper'da koşullu mantık olmadığı için tek "akıllı"
şablon yerine bu yol seçildi: maliyeti şablon sayısı, kazancı bir site HTML'ini
değiştirdiğinde yalnızca ilgili şablonun tamir edilmesi.

Tasarım gerekçelerinin tamamı için:
`docs/superpowers/specs/2026-08-05-obsidian-web-clipper-sablonlari-design.md`.

## Kurulum

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
| 2 | Ekşi Entry | regex: `eksisozluk.com/entry/<id>` | `2026-08-05 -- Eksi Entry -- Baslik Adi` |
| 2b | Ekşi Klip | regex: `eksisozluk.com/<baslik>--<id>` (başlık sayfası) | `2026-08-05 -- Eksi Klip -- Baslik Adi` |
| 3 | YouTube Video | URL öneki: `youtube.com/watch`, `m.youtube.com/watch`, `youtu.be/` | `2026-07-14 -- YouTube -- Video Basligi` |
| 4 | GitHub Repo | regex: `github.com/<kullanici>/<repo>` (alt sayfalar hariç) | `2026-08-05 -- GitHub -- kullanici-repo` |
| 5 | X (Twitter) Post | regex: `x.com` veya `twitter.com` üzerinde `/<handle>/status/<id>` | `2026-08-05 -- X -- kullanici_adi` |
| 6 | Reddit Post | regex: `reddit.com/r/<sub>/comments/...` | `2026-08-05 -- Reddit -- Gonderi Basligi` |
| 7 | Instagram Post | regex: `instagram.com/(p\|reel)/...` | `2026-08-05 -- Instagram -- Kullanici Adi` |
| 8 | LinkedIn Gönderi | regex: `linkedin.com/posts/...`, `linkedin.com/feed/update/...` | `2026-08-05 -- LinkedIn -- Ad Soyad` |
| 9 | Ürün | schema: `@Product` | `2026-08-05 -- Urun -- Urun Adi` |
| 10 | Makale | schema: `@Article`, `@NewsArticle`, `@BlogPosting`, `@TechArticle` | `2026-06-12 -- Makale -- Yazi Basligi` |

Tüm şablonlarda ortak: `path: "00 Inbox"`, `behavior: "create"`,
`type: referans` frontmatter alanı, `source`/`source_type` alanları, ve
gövdenin sonunda kullanıcının dolduracağı boş bir `## Notlar` bölümü.

## Eşleşme mekaniği

Web Clipper hangi şablonu kullanacağına şu sırayla karar veriyor
(`obsidianmd/obsidian-clipper` kaynağından doğrulandı, tahmin değil):

1. **URL öneki** — bir trie üzerinde en uzun eşleşme kazanır. Bu sette
   yalnızca YouTube'un tetikleyicileri bu türde.
2. **Regex** — `/^https:\/\/.../` biçimindeki tetikleyiciler. Ekşi Entry,
   GitHub, X, Reddit, Instagram, LinkedIn bu türde.
3. **Şema** — `schema:@Product`, `schema:@Article` gibi tetikleyiciler.
   **Yalnızca ilk iki kademe de başarısız olursa** denenir. Ürün ve Makale
   bu türde.

Kaynak: `src/utils/triggers.ts`.

**Kritik nokta:** hangi kademenin öne çıkacağını **liste sırası değil,
tetikleyici türü** belirliyor. Bu yüzden:

- LinkedIn'in regex tetikleyicisi, Makale'nin `@Article` şemasını **her zaman**
  yener — `templates/_order.json`'da Makale'nin LinkedIn'den sonra gelmesinin
  bir önemi yok, `linkedin.com/pulse/...` (ki bu `@Article` şeması taşır)
  yine de LinkedIn'e değil Makale'ye düşer çünkü LinkedIn'in regex'i
  `/posts/` ve `/feed/update/` yollarıyla sınırlı, `/pulse/` onu eşlemez.
- Liste sırası yalnızca **aynı kademedeki** şablonlar arasında karar veriyor.
  Bu sette bu yalnızca Ürün ile Makale için geçerli — ikisi de şema
  tetikleyicili. `_order.json`'da Ürün, Makale'den önce geliyor.

**Hiçbir tetikleyici eşleşmezse** `findMatchingTemplate` `undefined`
döndürür ve `src/core/popup.ts` içindeki fallback devreye girer:
`currentTemplate = templates[0]` — yani **listedeki ilk şablon**, liste
konumundan bağımsız bir "en son çare" değil, gerçekten dizinin sıfırıncı
elemanı. Bu yüzden `_order.json`'da Varsayılan ilk sırada: eşleşmeyen bir
sayfa Varsayılan'a değil de örneğin Ekşi Entry'ye düşmesin diye.

## `{{highlights}}` ve `{{content}}` üzerine notlar

Makale ve Varsayılan şablonları gövdenin başına kullanıcının klip sırasında
işaretlediği vurguları koyuyor:

```
{{highlights|map: item => item.content|blockquote}}
```

`{{highlights}}` bir dizi döndürür ve her elemanın metni **`text` değil
`content` anahtarında**, **HTML** biçiminde durur — bu yüzden `item.content`
okunuyor.

**Zincirin bu kısa hali bilinçli.** İlk sürüm `|join|markdown|callout` ile
"Vurgular" başlıklı bir kutu üretiyordu, ama hiçbir şey işaretlemeden
klipslediğinde notun başında boş bir kutu kalıyordu — 5 Ağustos 2026 canlı
testinde doğrulandı. Sebep: `map` bir **JSON dizisi** döndürüyor
(`src/utils/filters/map.ts` → `JSON.stringify`), `blockquote` bunu ayrıştırıp
boş dizide **hiçbir şey** basıyor, ama araya giren `join` diziyi düz metne
çeviriyor ve `callout` boş metinde bile kutu çatısını yazıyor. Diziyi
`blockquote`'a kadar bozmadan taşıyınca sorun kayboluyor.

Bedeli: vurgu metni HTML sarmalıyla (`<div>…</div>`) kalıyor. Obsidian satır
içi HTML'i sorunsuz render ediyor, sadece kaynak görünümde biraz gürültülü.

`{{content}}` bu vurgulardan bağımsız olarak sayfanın **tam metnini**
döndürmeye devam ediyor. Highlighter ayarı bu sette `highlight-inline`
olduğu için (bkz. `obsidian-web-clipper-settings.json` →
`highlighter_settings`), vurgular `{{content}}` içine `<mark>` olarak
gömülüyor, onun **yerine geçmiyor**. Yani "üstte vurgular, altta tam metin"
düzeninde bir miktar tekrar olması beklenen davranış, hata değil.

## Kırılganlık haritası

Her şablonun neye bağlı olduğu, o şablonun `noteContentFormat` ve
`properties` alanlarından okunuyor — aşağıdaki tablo tahmini değil, gerçek
dosyalardan çıkarıldı.

| Şablon | Bağımlılık | Bozulursa |
|---|---|---|
| Varsayılan | Genel sayfa çıkarımı: `{{title}}`, `{{author}}`, `{{site}}`, `{{description}}`, `{{content}}`, `{{highlights}}` | En dayanıklı şablon; sayfa çok atipikse tek tek alanlar boş gelebilir, tamamen boşalmaz |
| Ekşi Entry | DOM seçicileri: `a.entry-author`, `#entry-item-list li div.content` | Ekşi Sözlük arayüzü class/id değiştirirse yazar ve entry metni boş kalır |
| Ekşi Klip | DOM seçicisi: `#entry-item-list` (sayfadaki entry listesinin tamamı) | Aynı risk; ayrıca yalnızca **açık sayfadaki** entry'leri yakalar — başlığın tamamı için `eksi_export.py` script'i kullanılmalı |
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

Şablon kimlikleri (`id`) slug'dan deterministik üretiliyor
(`_id_uret` fonksiyonu, `build.py`) — bu yüzden her derlemede aynı id
çıkıyor ve yeniden import etmek eklentide kopya şablon yaratmıyor, mevcut
olanı güncelliyor.

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

## Canlı test sonuçları

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

**Düzeltmelerden sonra yeniden test edilmesi gerekenler:** bir Trendyol/Amazon
ürünü (fiyat ve marka dolu mu), bir tweet (gövdede metin var mı), bir Ekşi
başlık sayfası (Ekşi Klip devreye giriyor mu), vurgusuz bir makale (boş kutu
gitti mi). Ayrıca hiç denenmemiş üçlü: YouTube, LinkedIn gönderisi, Ekşi
permalink.

Test kriteri (bkz. tasarım dokümanı, "Test kriteri" bölümü): dosya adı
`YYYY-MM-DD -- {{Kaynak}} -- {{Başlık}}` desenine uyuyor mu, frontmatter
zorunlu alanları ve doğru `kaynak/*` etiketini taşıyor mu, gövdede boş kalan
`{{...}}` yer tutucusu var mı. Kırılgan üçlü (Instagram, LinkedIn, X) için
2. ve 3. koşulun kısmen sağlanması beklenebilir; bu durumda hangi alanın boş
kaldığı bu tabloya not düşülecek.
