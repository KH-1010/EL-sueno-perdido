#!/usr/bin/env node
/**
 * ╔══════════════════════════════════════════════════════════════════════════╗
 * ║  Arabic Games Advanced Scraper & Metadata Engine (v2.0 - Zero Lag CI)  ║
 * ║  مراقب ومحرك الألعاب العربية المتقدم — جلب أوتوماتيكي ذكي وتحديث الأرشيف  ║
 * ╚══════════════════════════════════════════════════════════════════════════╝
 * 
 * Features:
 * - Dual-Engine Scraper: Archive.org JSON Metadata API + Fallback HTML Parser
 * - Exponential Backoff & Auto-Retry for resilience against network/CI blips
 * - Smart Multi-Platform Detection (PS1, PS2, PS3, PSP, PS Vita, PS4, Switch, PC)
 * - Intelligent Deduplication & URI Merging
 * - Rich GitHub Actions Dashboard Summary ($GITHUB_STEP_SUMMARY)
 */

const fs   = require('fs');
const path = require('path');
const https = require('https');
const http  = require('http');

// ── CONFIGURATION ──────────────────────────────────────────────────────────
const SOURCES = [
  {
    id:       'dub',
    label:    'Arabic Dubbed (مدبلج)',
    archiveId: 'ArabicGamesDub515',
    url:      'https://archive.org/download/ArabicGamesDub515',
    metaUrl:  'https://archive.org/metadata/ArabicGamesDub515',
    jsonFile: path.join(__dirname, 'Dub.json'),
    defaultPlatform: 'ps2',
    type:     'dub',
  },
  {
    id:       'sub',
    label:    'Arabic Subbed (مترجم)',
    archiveId: 'Arabic_Games_Sub_515',
    url:      'https://archive.org/download/Arabic_Games_Sub_515',
    metaUrl:  'https://archive.org/metadata/Arabic_Games_Sub_515',
    jsonFile: path.join(__dirname, 'Sub.json'),
    defaultPlatform: 'ps2',
    type:     'sub',
  },
];

// Valid game archive & image extensions
const GAME_EXTS = /\.(iso|bin|img|pkg|rar|zip|7z|cue|chd|mdf|nsp|xci|cia|wud|wux|gcz|ciso|vpk|csao|pbp)$/i;

// ── NETWORK & RETRY ENGINE ────────────────────────────────────────────────
/**
 * Fetch URL with automatic exponential backoff and redirect resolution
 */
function fetchWithRetry(url, maxRetries = 3, delayMs = 1500) {
  return new Promise((resolve, reject) => {
    const attempt = (retryCount) => {
      const client = url.startsWith('https') ? https : http;
      const options = {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ArabicGamesScraper/2.0 (+https://github.com/KH-1010/EL-sueno-perdido)',
          'Accept': 'application/json, text/html, application/xhtml+xml, */*',
          'Cache-Control': 'no-cache',
        },
        timeout: 25000,
      };

      const req = client.get(url, options, (res) => {
        // Handle Redirects
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          let nextUrl = res.headers.location;
          if (!nextUrl.startsWith('http')) {
            const u = new URL(url);
            nextUrl = `${u.protocol}//${u.host}${nextUrl}`;
          }
          return fetchWithRetry(nextUrl, maxRetries, delayMs).then(resolve).catch(reject);
        }

        let data = '';
        res.setEncoding('utf8');
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode === 200) {
            resolve({ status: res.statusCode, body: data });
          } else if ((res.statusCode === 429 || res.statusCode >= 500) && retryCount < maxRetries) {
            console.warn(`   ⚠️ [HTTP ${res.statusCode}] Retrying in ${delayMs / 1000}s (Attempt ${retryCount + 1}/${maxRetries})...`);
            setTimeout(() => attempt(retryCount + 1), delayMs * Math.pow(1.8, retryCount));
          } else {
            resolve({ status: res.statusCode, body: data });
          }
        });
      });

      req.on('timeout', () => {
        req.destroy();
        if (retryCount < maxRetries) {
          console.warn(`   ⚠️ [Timeout] Connection timed out. Retrying in ${delayMs / 1000}s...`);
          setTimeout(() => attempt(retryCount + 1), delayMs * Math.pow(1.8, retryCount));
        } else {
          reject(new Error('Network request timed out after maximum retries.'));
        }
      });

      req.on('error', (err) => {
        if (retryCount < maxRetries) {
          console.warn(`   ⚠️ [Error: ${err.code || err.message}] Retrying in ${delayMs / 1000}s...`);
          setTimeout(() => attempt(retryCount + 1), delayMs * Math.pow(1.8, retryCount));
        } else {
          reject(err);
        }
      });
    };

    attempt(0);
  });
}

// ── SANITIZATION & METADATA HELPERS ───────────────────────────────────────
function cleanGameTitle(filename) {
  let t = decodeURIComponent(filename);
  // Remove file extension
  t = t.replace(GAME_EXTS, '');
  // Replace underscores, hyphens, plus signs with space
  t = t.replace(/[\-_\+]+/g, ' ');
  // Remove common noise tags
  t = t.replace(/\s*(arabic|arabi|ara|عربي|مدبلج|مترجم|dub|sub|dubbed|subbed|full|ver|version)\s*/gi, ' ');
  t = t.replace(/\s*(ARABIC|DUB|SUB|USA|EUR|JAP|PAL|NTSC)\s*/g, ' ');
  t = t.replace(/\(?\s*PS[1234]?|PSP|PSV|Vita|Switch|WiiU?\s*\)?/gi, '');
  // Clean up brackets and punctuation
  t = t.replace(/\[.*?\]|\(.*?\/.*?\)/g, ' ');
  t = t.replace(/\s+/g, ' ').trim();
  return t;
}

function detectPlatform(filename, title = '') {
  const f = `${filename} ${title}`.toLowerCase();
  if (/ps4|\.fpkg/.test(f))           return 'ps4';
  if (/ps3|rpcs3|psn|\.pkg/.test(f))  return 'ps3';
  if (/ps2/.test(f))                   return 'ps2';
  if (/ps1|psx|\.bin|\.cue|\.pbp/.test(f)) return 'ps1';
  if (/psp/.test(f))                   return 'psp';
  if (/vita|psv|\.vpk/.test(f))        return 'psvita';
  if (/switch|\.nsp|\.xci/.test(f))   return 'switch';
  if (/wiiu|\.wud|\.wux/.test(f))     return 'wiiu';
  if (/wii|\.gcz|\.ciso/.test(f))      return 'wii';
  if (/pc|\.exe|\.rar.*pc/.test(f))   return 'pc';
  return null;
}

function formatBytesToHuman(bytes) {
  if (!bytes || isNaN(bytes) || bytes <= 0) return '';
  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const idx = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, idx)).toFixed(2)} ${units[idx]}`;
}

function parseSizeStr(s) {
  if (!s) return '';
  if (typeof s === 'number' || /^\d+$/.test(String(s))) {
    return formatBytesToHuman(Number(s));
  }
  s = String(s).trim();
  return s.replace(/(\d+\.?\d*)\s*G$/i, '$1 GB')
          .replace(/(\d+\.?\d*)\s*M$/i, '$1 MB')
          .replace(/(\d+\.?\d*)\s*K$/i, '$1 KB');
}

// ── SCRAPING ENGINES ─────────────────────────────────────────────────────
/**
 * Engine 1: Archive.org Official JSON Metadata API (Fastest & Most Reliable)
 */
async function scrapeMetadataApi(source) {
  try {
    const { status, body } = await fetchWithRetry(source.metaUrl);
    if (status !== 200) return null;
    
    const data = JSON.parse(body);
    if (!data || !Array.isArray(data.files)) return null;

    const games = [];
    for (const f of data.files) {
      const filename = f.name || '';
      if (!GAME_EXTS.test(filename)) continue;

      const cleanTitle = cleanGameTitle(filename);
      if (!cleanTitle || cleanTitle.length < 2) continue;

      const downloadUrl = `${source.url}/${encodeURIComponent(filename)}`;
      const size = f.size ? formatBytesToHuman(f.size) : parseSizeStr(f.size);
      const date = f.mtime ? new Date(Number(f.mtime) * 1000).toISOString().split('T')[0] : '';

      games.push({ filename, cleanTitle, downloadUrl, date, size });
    }
    return games;
  } catch (err) {
    console.warn(`   ⚠️ [Metadata API Fallback] Could not parse JSON API: ${err.message}`);
    return null;
  }
}

/**
 * Engine 2: Archive.org HTML Table & Regex Parser (Robust Fallback)
 */
function scrapeHtmlPage(html, sourceUrl) {
  const games = [];
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
    games.push({ filename, cleanTitle, downloadUrl, date, size: parseSizeStr(size) });
  }

  if (games.length === 0) {
    const linkRegex = /href="(\/download\/[^"]+\/([^"?#]+\.(iso|bin|pkg|rar|zip|7z|chd|mdf|nsp|xci)))"[^>]*>([^<]*)<\/a>.*?<\/td>\s*<td[^>]*>([^<]*)<\/td>\s*<td[^>]*>([^<]*)<\/td>/gi;
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

// ── MERGE & SYNC ENGINE ──────────────────────────────────────────────────
function mergeAndSave(existingGames, scrapedGames, source) {
  const existingByUrl = {};
  const existingByTitle = {};
  
  existingGames.forEach(g => {
    (g.uris || []).forEach(u => { existingByUrl[u] = g; });
    if (g.title) existingByTitle[g.title.toLowerCase()] = g;
  });

  let added = 0;
  let updated = 0;

  scrapedGames.forEach(sg => {
    const url = sg.downloadUrl;
    if (existingByUrl[url]) {
      // Check if size or date needs refinement
      const entry = existingByUrl[url];
      if (!entry.fileSize && sg.size) { entry.fileSize = sg.size; updated++; }
      return;
    }
    
    const titleKey = sg.cleanTitle.toLowerCase();
    const existing = existingByTitle[titleKey];
    if (existing) {
      if (!existing.uris || !Array.isArray(existing.uris) || existing.uris.length === 0) {
        existing.uris = [url];
        updated++;
      } else if (!existing.uris.includes(url)) {
        existing.uris.push(url);
        updated++;
      }
      return;
    }

    const platform = detectPlatform(sg.filename, sg.cleanTitle) || source.defaultPlatform;
    const newEntry = {
      title:       sg.cleanTitle,
      uris:        [url],
      uploadDate:  sg.date || new Date().toISOString().split('T')[0],
      fileSize:    sg.size || 'N/A',
      platform:    platform,
      cover_url:   '',
      __source:    source.type
    };

    existingGames.push(newEntry);
    existingByTitle[titleKey] = newEntry;
    existingByUrl[url] = newEntry;
    added++;
  });

  // Sort alphabetically by Arabic/English title
  existingGames.sort((a, b) => (a.title || '').localeCompare(b.title || '', 'ar'));

  fs.writeFileSync(source.jsonFile, JSON.stringify(existingGames, null, 2), 'utf8');
  return { added, updated, total: existingGames.length };
}

// ── GITHUB ACTIONS DASHBOARD REPORTER ─────────────────────────────────────
function writeGitHubSummary(summaryRows) {
  const summaryFile = process.env.GITHUB_STEP_SUMMARY;
  if (!summaryFile) return;

  let md = `### 🤖 Arabic Games Scraper Execution Summary\n\n`;
  md += `| Source Database | New Games 🆕 | Updated Records 🔄 | Total Games 📦 | Status |\n`;
  md += `| :--- | :---: | :---: | :---: | :---: |\n`;
  
  for (const r of summaryRows) {
    const icon = r.error ? '❌ Error' : (r.added > 0 || r.updated > 0 ? '✨ Updated' : '✓ Clean');
    md += `| **${r.label}** | \`+${r.added}\` | \`~${r.updated}\` | **${r.total}** | ${icon} |\n`;
  }

  md += `\n*Last automated sync: ${new Date().toUTCString()}*\n`;
  
  try {
    fs.appendFileSync(summaryFile, md, 'utf8');
  } catch(e) {
    console.warn('Could not write to GitHub Step Summary:', e.message);
  }
}

// ── MAIN EXECUTION ────────────────────────────────────────────────────────
async function main() {
  console.log('\n╔══════════════════════════════════════════════════════════════╗');
  console.log('║  🎮 Arabic Games Advanced Scraper & Metadata Engine v2.0     ║');
  console.log('╚══════════════════════════════════════════════════════════════╝\n');

  let anyChanges = false;
  const summaryRows = [];

  for (const source of SOURCES) {
    console.log(`📦 [${source.label}] Inspecting Source: ${source.id}`);
    
    let existing = [];
    if (fs.existsSync(source.jsonFile)) {
      try {
        existing = JSON.parse(fs.readFileSync(source.jsonFile, 'utf8'));
        console.log(`   ✓ Loaded existing database: ${existing.length} records`);
      } catch (e) {
        console.warn(`   ⚠️ Error reading existing file, starting fresh: ${e.message}`);
      }
    }

    let scraped = null;
    // Attempt 1: Fast JSON Metadata API
    console.log(`   🔍 Querying Archive.org JSON Metadata API...`);
    scraped = await scrapeMetadataApi(source);

    if (scraped && scraped.length > 0) {
      console.log(`   ⚡ [API Success] Extracted ${scraped.length} games via structured metadata!`);
    } else {
      // Attempt 2: HTML Page Parsing Fallback
      console.log(`   🌐 [Fallback] Fetching HTML archive page: ${source.url}`);
      try {
        const { status, body } = await fetchWithRetry(source.url);
        console.log(`   ↳ HTTP Status: ${status} (${(body.length / 1024).toFixed(1)} KB)`);
        if (status === 200) {
          scraped = scrapeHtmlPage(body, source.url);
          console.log(`   ↳ [HTML Parser] Extracted ${scraped.length} games from page structure.`);
        } else if (status === 403 || status === 404) {
          console.log(`   ⚠️ Archive is restricted or hidden (HTTP ${status}). Retaining existing records.`);
          scraped = [];
        }
      } catch (err) {
        console.warn(`   ❌ [Network Error] Could not access source: ${err.message}`);
        scraped = [];
      }
    }

    const { added, updated, total } = mergeAndSave(existing, scraped || [], source);
    if (added > 0 || updated > 0) anyChanges = true;

    console.log(`   ✅ Result: +${added} New | ~${updated} Updated | Total Database: ${total}\n`);
    summaryRows.push({ label: source.label, added, updated, total });
  }

  console.log('━'.repeat(64));
  console.log(anyChanges ? '✨ Changes detected and saved successfully!' : '✓ Databases are fully up-to-date. No new entries.');
  
  // Write timestamp
  fs.writeFileSync(
    path.join(__dirname, '.scraper-last-run'),
    new Date().toISOString(),
    'utf8'
  );

  writeGitHubSummary(summaryRows);

  // Return exit code 1 if changes were made so CI/CD knows to commit
  process.exit(anyChanges ? 1 : 0);
}

main().catch(err => {
  console.error('\n❌ Fatal execution error:', err);
  process.exit(2);
});
