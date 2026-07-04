#!/usr/bin/env node
/**
 * ╔══════════════════════════════════════════════════════╗
 * ║  Arabic Games Scraper — مراقب ألعاب archive.org    ║
 * ║  يجلب قائمة الألعاب ويحدث Dub.json و Sub.json      ║
 * ╚══════════════════════════════════════════════════════╝
 */

const fs   = require('fs');
const path = require('path');
const https = require('https');

// ── CONFIG ─────────────────────────────────────────────
const SOURCES = [
  {
    id:       'dub',
    label:    'Arabic Dub',
    archiveId: 'ArabicGamesDub515',
    url:      'https://archive.org/download/ArabicGamesDub515',
    jsonFile: path.join(__dirname, 'Dub.json'),
    defaultPlatform: 'ps2',
    type:     'dub',
  },
  {
    id:       'sub',
    label:    'Arabic Sub',
    archiveId: 'Arabic_Games_Sub_515',
    url:      'https://archive.org/download/Arabic_Games_Sub_515',
    jsonFile: path.join(__dirname, 'Sub.json'),
    defaultPlatform: 'ps2',
    type:     'sub',
  },
];

// Game file extensions to capture
const GAME_EXTS = /\.(iso|bin|img|pkg|rar|zip|7z|cue|chd|mdf|nsp|xci|cia|wud|wux|gcz|ciso)$/i;

// ── HELPERS ────────────────────────────────────────────
function fetchText(url) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; ArabicGamesScraper/1.0)',
        'Accept': 'text/html,application/xhtml+xml,*/*',
      },
    };
    https.get(url, options, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return fetchText(res.headers.location).then(resolve).catch(reject);
      }
      let data = '';
      res.setEncoding('utf8');
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    }).on('error', reject);
  });
}

function cleanGameTitle(filename) {
  let t = decodeURIComponent(filename);
  // Remove extension
  t = t.replace(GAME_EXTS, '');
  // Remove common noise
  t = t.replace(/[\-_\+]+/g, ' ');
  t = t.replace(/\s*(arabic|arabi|ara|عربي|مدبلج|مترجم|dub|sub|dubbed|subbed)\s*/gi, ' ');
  t = t.replace(/\s*(ARABIC|DUB|SUB)\s*/g, ' ');
  t = t.replace(/\(?\s*PS[123]?\s*\)?/gi, '');
  t = t.replace(/\s+/g, ' ').trim();
  return t;
}

function detectPlatform(filename, title) {
  const f = (filename + ' ' + title).toLowerCase();
  if (/ps3|rpcs3|psn|\.pkg/.test(f))  return 'ps3';
  if (/ps1|psx|\.bin|\.cue/.test(f))  return 'ps1';
  if (/ps2/.test(f))                   return 'ps2';
  if (/wii|wiiu|\.wud|\.wux/.test(f)) return 'wiiu';
  if (/pc|\.exe|\.rar.*pc/.test(f))   return 'pc';
  if (/switch|\.nsp|\.xci/.test(f))   return 'switch';
  return null; // will use default
}

function parseSizeStr(s) {
  if (!s) return '';
  s = s.trim();
  // Normalize: "1.5G" → "1.5 GB", "845.0M" → "845 MB"
  return s.replace(/(\d+\.?\d*)\s*G$/i, '$1 GB')
          .replace(/(\d+\.?\d*)\s*M$/i, '$1 MB')
          .replace(/(\d+\.?\d*)\s*K$/i, '$1 KB');
}

/**
 * Parse archive.org download page HTML to extract file list
 */
function parseArchivePage(html, sourceUrl) {
  const games = [];
  
  // Match table rows in archive.org download page
  // Pattern: <tr><td><a href="filename">filename</a></td><td>date</td><td>size</td>...
  const rowRegex = /<tr[^>]*>\s*<td[^>]*>\s*<a\s+href="([^"]+)"[^>]*>([^<]+)<\/a>\s*<\/td>\s*<td[^>]*>([^<]*)<\/td>\s*<td[^>]*>([^<]*)<\/td>/gi;
  
  let match;
  while ((match = rowRegex.exec(html)) !== null) {
    const href     = match[1];
    const filename = decodeURIComponent(match[2].trim());
    const date     = match[3].trim();
    const size     = match[4].trim();
    
    if (!GAME_EXTS.test(filename)) continue;
    
    const cleanTitle = cleanGameTitle(filename);
    if (!cleanTitle || cleanTitle.length < 2) continue;
    
    const downloadUrl = href.startsWith('http') ? href : `${sourceUrl}/${encodeURIComponent(filename)}`;
    
    games.push({
      filename,
      cleanTitle,
      downloadUrl,
      date: date || '',
      size: parseSizeStr(size),
    });
  }

  // Fallback: simpler regex for different page layouts
  if (games.length === 0) {
    const linkRegex = /href="(\/download\/[^"]+\/([^"?#]+\.(iso|bin|pkg|rar|zip|7z|chd|mdf)))"[^>]*>([^<]*)<\/a>.*?<\/td>\s*<td[^>]*>([^<]*)<\/td>\s*<td[^>]*>([^<]*)<\/td>/gi;
    while ((match = linkRegex.exec(html)) !== null) {
      const href     = `https://archive.org${match[1]}`;
      const filename = decodeURIComponent(match[2]);
      const date     = match[5]?.trim() || '';
      const size     = match[6]?.trim() || '';
      
      const cleanTitle = cleanGameTitle(filename);
      if (!cleanTitle || cleanTitle.length < 2) continue;
      
      games.push({ filename, cleanTitle, downloadUrl: href, date, size: parseSizeStr(size) });
    }
  }

  return games;
}

/**
 * Load existing JSON, merge with scraped data, save back
 */
function mergeAndSave(existingGames, scrapedGames, source) {
  // Build index of existing entries by download URL
  const existingByUrl = {};
  const existingByTitle = {};
  existingGames.forEach(g => {
    (g.uris || []).forEach(u => { existingByUrl[u] = g; });
    existingByTitle[g.title?.toLowerCase()] = g;
  });

  let added   = 0;
  let updated = 0;

  scrapedGames.forEach(sg => {
    const url = sg.downloadUrl;
    
    // Already exists by URL → skip (preserve user edits)
    if (existingByUrl[url]) return;
    
    // Check if same title exists → update URL if missing
    const titleKey = sg.cleanTitle.toLowerCase();
    const existing = existingByTitle[titleKey];
    if (existing) {
      // Only add URL if uris array is empty
      if (!existing.uris || existing.uris.length === 0) {
        existing.uris = [url];
        updated++;
      }
      return;
    }

    // New game — add it
    const platform = detectPlatform(sg.filename, sg.cleanTitle) || source.defaultPlatform;
    existingGames.push({
      title:       sg.cleanTitle,
      uris:        [url],
      uploadDate:  sg.date,
      fileSize:    sg.size,
      platform,
      cover_url:   '',
    });
    existingByTitle[titleKey] = existingGames[existingGames.length - 1];
    added++;
  });

  // Sort by title
  existingGames.sort((a, b) => (a.title || '').localeCompare(b.title || '', 'ar'));

  fs.writeFileSync(source.jsonFile, JSON.stringify(existingGames, null, 2), 'utf8');
  return { added, updated, total: existingGames.length };
}

// ── MAIN ───────────────────────────────────────────────
async function main() {
  console.log('\n🎮 Arabic Games Scraper — بدء المراقبة\n');
  console.log('━'.repeat(50));

  let anyChanges = false;

  for (const source of SOURCES) {
    console.log(`\n📦 [${source.label}] جارٍ جلب: ${source.url}`);
    
    // Load existing JSON
    let existing = [];
    if (fs.existsSync(source.jsonFile)) {
      try {
        existing = JSON.parse(fs.readFileSync(source.jsonFile, 'utf8'));
        console.log(`   ✓ ملف موجود: ${existing.length} لعبة`);
      } catch (e) {
        console.warn(`   ⚠ خطأ في قراءة الملف: ${e.message}`);
      }
    }

    // Fetch archive.org page
    let scraped = [];
    try {
      const { status, body } = await fetchText(source.url);
      console.log(`   ↳ HTTP ${status}, الحجم: ${(body.length / 1024).toFixed(1)} KB`);
      
      if (status === 200) {
        scraped = parseArchivePage(body, source.url);
        console.log(`   ↳ تم استخراج: ${scraped.length} لعبة من الصفحة`);
      } else if (status === 403 || status === 404) {
        console.log(`   ⚠ الأرشيف مخفي (is_dark) — لا يمكن الوصول تلقائياً`);
        console.log(`   ℹ سيتم الاحتفاظ بالملف الحالي دون تغيير`);
      }
    } catch (err) {
      console.warn(`   ✗ فشل الاتصال: ${err.message}`);
    }

    // Merge & save
    const { added, updated, total } = mergeAndSave(existing, scraped, source);
    if (added > 0 || updated > 0) anyChanges = true;
    
    console.log(`   ✅ النتيجة: +${added} جديدة | ~${updated} محدَّثة | المجموع: ${total}`);
  }

  console.log('\n' + '━'.repeat(50));
  console.log(anyChanges ? '\n✅ تم حفظ التغييرات!' : '\n✓ لا يوجد جديد — الملفات محدَّثة');
  
  // Write last-run timestamp
  fs.writeFileSync(
    path.join(__dirname, '.scraper-last-run'),
    new Date().toISOString(),
    'utf8'
  );

  // Exit with code 1 if changes (GitHub Actions can use this to decide commit)
  process.exit(anyChanges ? 1 : 0);
}

main().catch(err => {
  console.error('\n❌ خطأ غير متوقع:', err);
  process.exit(2);
});
