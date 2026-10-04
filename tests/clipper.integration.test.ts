// @vitest-environment jsdom
// Resmî obsidian-clipper checkout'unda src/utils/ altına kopyalanarak çalışır.
// CLIPPER_TEMPLATE_ROOT bu projenin kökünü gösterir; README'deki komuta bakın.
import { expect, test, vi, beforeEach, afterEach } from 'vitest';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { compileTemplate } from './template-compiler';
import { buildVariables } from './shared';
import Defuddle from 'defuddle';
import { createAsyncResolver, createSelectorProcessor } from '../api';
import { initializeTriggers, findMatchingTemplate } from './triggers';

const root = process.env.CLIPPER_TEMPLATE_ROOT!;
const load = (slug: string) => JSON.parse(readFileSync(join(root, 'templates', slug + '.json'), 'utf8'));
const order = JSON.parse(readFileSync(join(root, 'templates/_order.json'), 'utf8'));
initializeTriggers(order.map(load));
beforeEach(() => { vi.spyOn(console, 'error'); });
afterEach(() => {
  // Motor hatalarda boş çıktı döndürebiliyor; sessiz bir geçişe izin verme.
  expect(console.error).not.toHaveBeenCalled();
  vi.restoreAllMocks();
});

async function render(slug: string, data: any = {}, html = '') {
  const template = load(slug);
  const url = data.url || 'https://example.com/page';
  const schemaOrgData = data.schemaOrgData ? [data.schemaOrgData].flat() : undefined;
  const variables = buildVariables({title: '', url, ...data, schemaOrgData});
  variables['{{date}}'] = '2026-09-06T12:00:00+03:00';
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const compile = (text: string) => compileTemplate(0, text, variables, url,
    createAsyncResolver(doc), createSelectorProcessor(doc));
  const props: Record<string, string> = {};
  for (const p of template.properties) props[p.name] = await compile(p.value);
  return {name: await compile(template.noteNameFormat), body: await compile(template.noteContentFormat), props};
}

test.each([
  ['https://github.com/obsidianmd/obsidian-clipper', 'GitHub Repo'],
  ['https://github.com/obsidianmd/obsidian-clipper?tab=readme-ov-file', 'GitHub Repo'],
  ['https://github.com/obsidianmd/obsidian-clipper#readme', 'GitHub Repo'],
  ['https://github.com/obsidianmd/obsidian-clipper/issues/12', 'Teknik Dokümantasyon'],
  ['https://github.com/obsidianmd/obsidian-clipper/pull/12', 'Teknik Dokümantasyon'],
  ['https://www.linkedin.com/jobs/view/123456/', 'İş İlanı'],
  ['https://www.linkedin.com/posts/example', 'LinkedIn Gönderi'],
  ['https://help.obsidian.md/web-clipper/logic', 'Teknik Dokümantasyon'],
  ['https://github.com.evil.example/owner/repo', undefined],
  ['https://github.com/owner/repo/issues', undefined],
])('URL %s → %s', async (url, name) => {
  expect((await findMatchingTemplate(url, async () => []))?.name).toBe(name);
});

test.each(['is-ilani', 'teknik-dokumantasyon'])('yeni şablon mevcut: %s', slug => {
  expect(existsSync(join(root, 'templates', slug + '.json'))).toBe(true);
});

test('JobPosting genel makaleden önce seçilir', async () => {
  expect((await findMatchingTemplate('https://example.org/careers/123', async () => [
    {'@type': 'Article'}, {'@type': 'JobPosting'}
  ]))?.name).toBe('İş İlanı');
});

test('aynı yazara ait farklı X gönderileri farklı ad alır', async () => {
  const a = await render('x', {url: 'https://x.com/example/status/123'});
  const b = await render('x', {url: 'https://x.com/example/status/456?ref=share'});
  expect(a.name).not.toBe(b.name);
  expect(a.name).toContain('123');
  expect(b.name).toContain('456');
  expect(a.props.author).toBe('example');
});

test('aynı başlıktaki farklı entry adları çakışmaz ve takip parametresi kimliğe girmez', async () => {
  const a = await render('eksi-entry', {url: 'https://eksisozluk.com/entry/123', title: 'Aynı başlık'});
  const b = await render('eksi-entry', {url: 'https://eksisozluk.com/entry/456?ref=share', title: 'Aynı başlık'});
  expect(a.name).not.toBe(b.name);
  expect(b.props.entry_id).toBe('456');
});

test.each(['linkedin', 'instagram'])('%s seçim yapıldığında feed yerine seçimi kaydeder', async slug => {
  const r = await render(slug, {selection: 'Seçtiğim metin', content: 'Reklamlı feed'});
  expect(r.body).toContain('Seçtiğim metin');
  expect(r.body).not.toContain('Reklamlı feed');
  expect(r.props.title).not.toBe('');
});

test.each(['youtube', 'makale', 'reddit'])('%s eksik metadata ile kullanılabilir başlık ve tarih üretir', async slug => {
  const r = await render(slug, {title: 'Yedek başlık'});
  expect(r.name).toContain('2026-09-06');
  expect(r.name).toContain('Yedek başlık');
  expect(r.props.title).toBe('Yedek başlık');
  expect(r.props.date).toBe('2026-09-06');
});

test('yorum yoksa Reddit boş yorum bölümü üretmez', async () => {
  expect((await render('reddit')).body).not.toContain('### İlk Yorum');
});

test('ilan şema verilerini korur, maaş uydurmaz', async () => {
  const r = await render('is-ilani', {schemaOrgData: {'@type': 'JobPosting', title: 'Support Engineer',
    hiringOrganization: {name: 'Example'}, employmentType: 'FULL_TIME', jobLocationType: 'TELECOMMUTE',
    validThrough: '2026-10-01', description: '<p>Teknik destek</p>'}});
  expect(r.props.title).toBe('Support Engineer');
  expect(r.props.company).toBe('Example');
  expect(r.props.salary).toBe('');
  expect(r.props.deadline).toBe('2026-10-01');
  expect(r.body).toContain('Teknik destek');
});

test('ilan maaş aralığı, para birimi ve dönemini birlikte taşır', async () => {
  const r = await render('is-ilani', {schemaOrgData: {'@type':'JobPosting',
    baseSalary: {currency:'EUR', value:{minValue:40000, maxValue:50000, unitText:'YEAR'}}}});
  expect(r.props.salary).toContain('40000');
  expect(r.props.salary).toContain('50000');
  expect(r.props.salary).toContain('EUR');
  expect(r.props.salary).toContain('YEAR');
  expect(r.props.salary).toBe('40000 – 50000 EUR / YEAR');
});

test('teknik doküman kod bloklarını korur', async () => {
  const content = 'Kurulum\n\n```bash\npython3 build.py\n```';
  const r = await render('teknik-dokumantasyon', {title: 'Kurulum', content});
  expect(r.body).toContain(content);
});

test('gerçek HTML ve JSON-LD ilan verilerini nota taşır', async () => {
  const html = `<html><head><title>Support Engineer</title>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"JobPosting",
    "title":"Support Engineer","hiringOrganization":{"@type":"Organization","name":"Example"},
    "description":"<p>Linux deneyimi</p>","jobLocation":{"@type":"Place","address":{
    "@type":"PostalAddress","addressLocality":"İstanbul","addressCountry":"TR"}}}</script>
    </head><body><article><h1>Support Engineer</h1><p>Linux deneyimi</p></article></body></html>`;
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const extracted = new Defuddle(doc, {url: 'https://example.org/jobs/42'}).parse();
  const result = await render('is-ilani', extracted, html);
  expect(result.props.company).toBe('Example');
  expect(result.props.location).toBe('İstanbul, TR');
  expect(result.body).toContain('Linux deneyimi');
  expect(result.body).not.toMatch(/\{[{%]/);
});

test('GitHub takip parametreleri ve sondaki slash ad ve repo alanına taşınmaz', async () => {
  const r = await render('github', {url: 'https://github.com/owner/repo/?tab=readme#intro'});
  expect(r.props.repo).toBe('owner/repo');
  expect(r.name).toBe('2026-09-06 -- GitHub -- owner-repo');
});

test('ürün eksik fiyat ve puan için boş tablo satırı üretmez', async () => {
  const r = await render('urun', {title: 'Örnek ürün'});
  expect(r.props.title).toBe('Örnek ürün');
  expect(r.body).not.toContain('**Fiyat**');
  expect(r.body).not.toContain('**Puan**');
});

test('tüm şablonlar boş sayfa verileriyle ifadeleri çözer', async () => {
  for (const slug of order) {
    const r = await render(slug);
    expect(r.name).not.toMatch(/Invalid Date|\{[{%]/);
    expect(r.body).not.toMatch(/\{[{%]/);
    expect(r.props.title).not.toBe('');
  }
});
