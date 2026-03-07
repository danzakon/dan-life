# Programmatic Access to YouTube Watch Later Playlist

Research completed 2026-03-07. Focused on what actually works today.

---

## TL;DR

```
                        YouTube Watch Later Access Methods
  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │   YouTube Data API (v3)         BLOCKED since Sept 2016             │
  │   ─────────────────────         Returns empty list for WL/HL       │
  │                                                                     │
  │   yt-dlp + cookies              WORKS (best CLI option)             │
  │   ────────────────────          --cookies-from-browser or file     │
  │                                                                     │
  │   yt-playlist-export            WORKS (wrapper around yt-dlp)       │
  │   ──────────────────            pip install, outputs JSON/CSV      │
  │                                                                     │
  │   Browser console scrape        WORKS (manual but reliable)         │
  │   ────────────────────────      JS in DevTools, outputs JSON       │
  │                                                                     │
  │   Chrome extensions             WORKS (easiest for non-devs)        │
  │   ─────────────────             Export to CSV/JSON                  │
  │                                                                     │
  │   Google Takeout                PARTIAL (playlists yes, WL unclear) │
  │   ──────────────────            HTML/JSON export, slow             │
  │                                                                     │
  │   Playwright/Selenium           WORKS (heavy, but automatable)      │
  │   ────────────────────────      Full browser automation            │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
```

**Recommended path:** `yt-dlp` with `--cookies-from-browser` for CLI automation, or the `yt-playlist-export` Python package for a cleaner wrapper. Both require browser cookies because the YouTube API itself is permanently locked.

---

## 1. YouTube Data API v3 -- Permanently Blocked

### The History

On **September 12, 2016**, Google disabled API access to Watch Later (`WL`) and Watch History (`HL`) playlists. This is documented in the official [YouTube Data API revision history](https://developers.google.com/youtube/v3/revision_history#september-15-2016):

> "Requests to retrieve playlist details (playlists.list) for a channel's watch history or watch later playlist will return an empty list after September 12, 2016. Requests to retrieve playlist items (playlistItems.list) in either of those playlists will also return an empty list after that time. This is true for the new values, HL and WL, as well as for any watch history or watch later playlist IDs that your API Client may have already stored."

### Current State (2025-2026)

**Nothing has changed.** The API still returns empty lists for `WL` and `HL` playlist IDs, even with full OAuth2 authentication. This is a deliberate policy decision, not a bug. There is no workaround using the official API.

Confirmed by:
- [StackOverflow: Youtube API getting Watch Later Playlist](https://stackoverflow.com/questions/41451533/youtube-api-getting-watch-later-playlist) (multiple answers over 8 years, all confirming it's blocked)
- [MichaelCade/youtube-watch-later-mess](https://github.com/MichaelCade/youtube-watch-later-mess) (Jan 2025): Author confirms API does not work, had to resort to browser scraping + API hybrid approach

### What the API CAN Do

You can still use the YouTube Data API to:
- List and manage **user-created playlists** (not WL/HL)
- Create new playlists and add videos to them
- Read video metadata for known video IDs
- Search for videos

This means: if you can get the video IDs from Watch Later via another method, you can use the API to create organized playlists from them. This is exactly the hybrid approach MichaelCade uses.

---

## 2. yt-dlp and Watch Later

### Does It Work?

**Yes**, yt-dlp can access the Watch Later playlist. It is the most reliable CLI tool for this.

### Authentication Required

Watch Later is a private playlist, so yt-dlp needs your YouTube session cookies. Two methods:

#### Method A: `--cookies-from-browser` (Easier)

```bash
yt-dlp --cookies-from-browser chrome \
  --flat-playlist \
  --print "%(playlist_index)s %(original_url)s %(title)s - %(uploader)s [%(duration_string)s]" \
  "https://www.youtube.com/playlist?list=WL"
```

| Flag | Purpose |
|------|---------|
| `--cookies-from-browser chrome` | Reads cookies directly from your Chrome browser's cookie database |
| `--flat-playlist` | Lists videos without downloading them |
| `--print "..."` | Custom output format for each video entry |

Supported browsers: `chrome`, `firefox`, `safari`, `brave`, `edge`, `opera`, `vivaldi`, `whale`, `chromium`

You can also specify a profile: `--cookies-from-browser "chrome:Profile 1"`

**Gotcha:** Chrome must not be running when yt-dlp reads cookies (it locks the database). On macOS, you can add Chrome launch flags to allow concurrent access, but it's fragile. Alternatively, use a separate Chrome profile dedicated to this purpose.

#### Method B: Cookie File (More Reliable for Automation)

Export cookies to a Netscape-format file, then:

```bash
yt-dlp --cookies /path/to/cookies.txt \
  --flat-playlist \
  --print-to-file webpage_url urls.txt \
  "https://www.youtube.com/playlist?list=WL"
```

### Exporting Cookies Properly (Critical)

YouTube rotates cookies aggressively on open browser tabs. The [yt-dlp wiki](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies) has a specific procedure:

1. Open a **private/incognito** window
2. Log into YouTube
3. In the **same window and same tab**, navigate to `https://www.youtube.com/robots.txt`
4. Export `youtube.com` cookies using a browser extension (e.g., "Get cookies.txt LOCALLY")
5. **Close the incognito window immediately** so YouTube never rotates those session cookies

**Do NOT** use `--cookies COOKIEFILE --cookies-from-browser BROWSER` together -- this exports your regular browser cookies, not the incognito session.

### Cookie Expiration

Cookies exported this way can last for weeks or longer, as long as the session is never opened in a browser again. If the incognito window is closed immediately after export, YouTube has no opportunity to rotate the cookies.

### OAuth2 Status

As of late 2024, **YouTube OAuth2 login via yt-dlp no longer works** due to new restrictions. Cookie-based auth is the only supported method.

### Practical Limits

- Large playlists (1000+ videos) may hit rate limits or cookie expiration mid-download
- EposVox reports that for 5000+ video Watch Later lists, cookies can expire after ~100 videos, requiring the URL extraction approach:

```bash
# Step 1: Extract all URLs to a file (fast, flat listing)
yt-dlp "https://www.youtube.com/playlist?list=WL" \
  --skip-download --ignore-errors --flat-playlist \
  --print-to-file webpage_url urls.txt \
  --cookies-from-browser chrome

# Step 2: Download from the URL list (can be done in batches)
yt-dlp -a urls.txt
```

### PO Token

YouTube is gradually requiring a "PO Token" for downloading actual videos. This doesn't affect playlist metadata extraction (titles, URLs, etc.), but matters if you want to download the video files themselves. See the [yt-dlp PO Token Guide](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide).

---

## 3. Browser Cookie Export Approach

### Overview

The cookie export approach works because Watch Later is rendered as a standard playlist page at `https://www.youtube.com/playlist?list=WL`. Any tool that can present valid YouTube session cookies can access it.

### Step-by-Step (Chrome)

1. Install the "Get cookies.txt LOCALLY" Chrome extension (or equivalent)
2. Open an incognito window
3. Log into YouTube
4. Navigate to `https://www.youtube.com/robots.txt` (simple page, prevents cookie rotation)
5. Click the extension icon and export cookies for `youtube.com`
6. Save as `cookies.txt` (Netscape format)
7. Close the incognito window immediately
8. Use with yt-dlp: `yt-dlp --cookies cookies.txt ...`

### Cookie File Format

The exported file is Netscape HTTP Cookie format:

```
# Netscape HTTP Cookie File
.youtube.com    TRUE    /    TRUE    1710000000    __Secure-3PAPISID    <value>
.youtube.com    TRUE    /    TRUE    1710000000    __Secure-3PSID      <value>
.youtube.com    TRUE    /    TRUE    1710000000    SAPISID             <value>
...
```

### Security Considerations

- These cookies grant full access to your YouTube/Google account
- Store them securely (encrypted disk, not in git)
- Consider using a throwaway/dedicated Google account
- Delete the cookie file when done

---

## 4. Google Takeout

### What You Get

Google Takeout (`takeout.google.com`) can export YouTube data including:
- Watch history (as HTML or JSON)
- Playlists (including playlist video lists)
- Subscriptions
- Comments
- Liked videos

### Watch Later Specifically

Google Takeout exports playlists, but the **Watch Later playlist has inconsistent support** in Takeout. Some users report getting it, others report it being excluded. The data Google exports for playlists is typically:

- A CSV or JSON file listing playlists
- For each playlist, video IDs and titles
- Watch history comes as an HTML file with links and timestamps

### Format Example (Playlists)

```
YouTube and YouTube Music/
  playlists/
    Watch later.csv          # Sometimes present
    My Playlist Name.csv
  history/
    watch-history.html       # or .json
```

### Limitations

- **Slow:** Export can take minutes to hours depending on data size
- **Not real-time:** It's a snapshot, not a live connection
- **Inconsistent:** Watch Later may or may not be included
- **No automation:** Must be triggered manually through the web UI (no API for Takeout itself)

### Verdict

Takeout is a fallback for one-time exports but not viable for any kind of ongoing automation. The delay and manual process make it impractical compared to yt-dlp.

---

## 5. Browser Extensions

### Extensions That Export Watch Later

| Extension | Platform | Output | Users | Notes |
|-----------|----------|--------|-------|-------|
| **YouTube Watch Later Tool (Export & Remove)** | Chrome | CSV | 45 | Export all or selected videos |
| **YT Watch Later Assist** | Chrome | N/A | 40,000 | Bulk add/delete, no export |
| **YouTube Watch Later Organizer** | Chrome | N/A | 175 | Categorizes by topic |
| **yt-watchlater-exporter** | Chrome (dev) | JSON | 0 (GitHub) | Open source, MIT license |

### yt-watchlater-exporter (Open Source)

From [afnan-nex/yt-watchlater-exporter](https://github.com/afnan-nex/yt-watchlater-exporter):

- Chrome extension (load unpacked in developer mode)
- Opens Watch Later page, waits 5 seconds for content to load
- Scrapes `ytd-playlist-video-renderer` elements
- Exports as JSON with `title` and `url` fields
- Simple, auditable code

### YouTube Watch Later Tool

From Chrome Web Store -- commercial extension that can:
- Export all Watch Later videos to CSV
- Export selected videos to CSV
- Remove all or selected videos
- Add entire playlists to Watch Later

### Limitation

All browser extensions share the same fundamental approach: they inject JavaScript into the Watch Later page and scrape the DOM. This means they require:
- Being logged in to YouTube in the browser
- The Watch Later page to be open
- Manual triggering (click a button)

Not suitable for headless/automated workflows.

---

## 6. Console JavaScript Scraping

### The MichaelCade Approach

This is the most transparent and auditable method. From [MichaelCade/youtube-watch-later-mess](https://github.com/MichaelCade/youtube-watch-later-mess):

1. Open Watch Later playlist in Chrome
2. Open DevTools Console
3. Run this script to scroll through and extract all videos:

```javascript
async function scrollAndExtractVideosWithDebug() {
    let prevVideoCount = 0;

    // Scroll until all videos are loaded
    while (true) {
        window.scrollTo(0, document.documentElement.scrollHeight);
        await new Promise(resolve => setTimeout(resolve, 2000));

        let videos = document.querySelectorAll('ytd-playlist-video-renderer');
        console.log(`Videos loaded: ${videos.length}`);

        if (videos.length === prevVideoCount) break;
        prevVideoCount = videos.length;
    }

    console.log(`Finished scrolling! Total videos detected: ${prevVideoCount}`);

    let videoElements = Array.from(
        document.querySelectorAll('ytd-playlist-video-renderer')
    );
    let data = videoElements.map((video, index) => {
        let title = video.querySelector('#video-title')?.textContent.trim()
            || 'Unknown Title';
        let link = video.querySelector('#video-title')?.href || '#';
        let ariaLabel = video.querySelector('h3')?.getAttribute('aria-label')
            || '';
        return { index: index + 1, title, link, ariaLabel };
    });

    console.log(`Extracted ${data.length} videos.`);
    console.log(JSON.stringify(data, null, 2));
    return data;
}

scrollAndExtractVideosWithDebug();
```

4. Copy the JSON output and save to a file

### Output Format

```json
[
  {
    "index": 1,
    "title": "MySQL Tutorial",
    "link": "https://www.youtube.com/watch?v=yPu6qV5byu4&list=WL&index=1",
    "ariaLabel": "MySQL Tutorial by Derek Banas 1,743,455 views 10 years ago 41 minutes"
  }
]
```

The `ariaLabel` field is useful because it contains channel name, view count, upload age, and duration in one string.

### Hybrid Approach

MichaelCade's full workflow:
1. Scrape Watch Later with the JS console script (get `scrape.json`)
2. Use YouTube Data API v3 (with OAuth) to **create new playlists** and **add videos to them**
3. Go program reads `scrape.json`, categorizes videos by keyword, and creates organized playlists via the API

This is clever: you can't *read* Watch Later via API, but you can *write* to other playlists. So scrape the data out, then use the API to organize it.

---

## 7. Selenium/Playwright Automation

### Is It Viable?

Yes, and it's the approach that most closely mirrors "log in and scrape the page." Playwright is the modern choice over Selenium.

### Approach

```
┌──────────────────────────────────────────────────────────┐
│                 Playwright Automation Flow                 │
│                                                           │
│  1. Launch browser with saved auth state                  │
│  2. Navigate to youtube.com/playlist?list=WL              │
│  3. Wait for playlist to render                           │
│  4. Scroll to bottom (lazy loading)                       │
│  5. Extract video data from DOM                           │
│  6. Output as JSON/CSV                                    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Key Considerations

| Factor | Details |
|--------|---------|
| **Auth** | Use Playwright's `storageState` to save/restore login session |
| **Lazy loading** | Must scroll to load all videos (same as console approach) |
| **Rate limiting** | YouTube may serve bot detection CAPTCHAs |
| **Breakage** | DOM selectors change when YouTube updates their frontend |
| **Headless** | Can run headless, but YouTube is more likely to flag headless browsers |
| **Speed** | Slow compared to yt-dlp (full browser rendering) |
| **Dependencies** | Requires browser binaries, heavier than yt-dlp |

### When To Use Playwright

- If yt-dlp cookie auth is broken/unreliable
- If you need to interact with the page (e.g., remove videos after processing)
- If you want to build a custom UI/workflow around it
- If you need data that yt-dlp doesn't expose

### Existing Tool: yt-playlist-export (Simpler)

Before building a Playwright solution, try [yt-playlist-export](https://github.com/daydiff/yt-playlist-export) first:

```bash
pip install yt-playlist-export

# Export Watch Later to JSON using Chrome cookies
yt-playlist-export --browser chrome -f json -o watch-later.json \
  "https://www.youtube.com/playlist?list=WL"

# Or using a cookie file
yt-playlist-export --cookies /path/to/cookies.txt -f csv -o watch-later.csv \
  "https://www.youtube.com/playlist?list=WL"
```

This is a yt-dlp wrapper that outputs clean JSON or CSV. Supports all browsers that yt-dlp supports for cookie extraction.

---

## 8. Comparison: X Bookmarks (xquery) vs YouTube Watch Later

```
┌─────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│                         │  X Bookmarks (xquery)        │  YouTube Watch Later         │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Official API access     │ Yes (with OAuth)             │ NO (blocked since 2016)      │
│ Auth method             │ OAuth 2.0 tokens             │ Browser cookies only         │
│ CLI tool                │ xquery                       │ yt-dlp / yt-playlist-export  │
│ Data format             │ JSON via API                 │ JSON/CSV via scraping        │
│ Rate limits             │ Twitter API rate limits      │ YouTube cookie expiration    │
│ Token refresh           │ OAuth refresh tokens         │ Manual cookie re-export      │
│ Automation difficulty   │ Low (standard OAuth flow)    │ Medium (cookie management)   │
│ Reliability             │ High (official API)          │ Medium (unofficial methods)  │
│ Headless operation      │ Yes                          │ Yes (with cookie file)       │
│ Session persistence     │ OAuth tokens last long       │ Cookies expire in days/weeks │
└─────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

### The Gap

The X bookmarks workflow via `xquery` is clean:
1. Authenticate once with OAuth
2. Use refresh tokens to maintain access indefinitely
3. CLI fetches bookmarks as structured JSON

YouTube Watch Later has no equivalent because the API is blocked. The closest equivalent workflow would be:

```
Equivalent YouTube Watch Later Workflow
────────────────────────────────────────

1. Install yt-playlist-export:
   pip install yt-playlist-export

2. Export cookies from incognito session (one-time, repeat when expired)

3. Fetch Watch Later:
   yt-playlist-export --cookies cookies.txt -f json -o wl.json \
     "https://www.youtube.com/playlist?list=WL"

4. Parse the JSON output into your pipeline

5. Re-export cookies every 1-2 weeks when they expire
```

### The Friction Point

The fundamental difference is **cookie management**. OAuth tokens can be refreshed programmatically. Browser cookies cannot -- they require a human to log in via a browser. This is the core limitation.

Possible mitigations:
- Use `--cookies-from-browser` with a dedicated browser profile that stays logged in
- Run `yt-dlp --cookies-from-browser chrome --cookies cookies.txt` periodically as a cron job to refresh the cookie file (note: this has caveats, see yt-dlp issue #11773)
- Accept manual cookie refresh every 1-2 weeks as part of a weekly review process

---

## 9. Recommended Architecture

For a pipeline that mirrors the X bookmarks workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                   YouTube Watch Later Pipeline                   │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │  Cookie       │    │  yt-playlist-    │    │  Pipeline     │  │
│  │  Management   │───▶│  export          │───▶│  Integration  │  │
│  │              │    │                  │    │               │  │
│  │  - Incognito │    │  - --cookies     │    │  - Parse JSON │  │
│  │    export    │    │  - -f json       │    │  - Categorize │  │
│  │  - Dedicated │    │  - WL playlist   │    │  - Store      │  │
│  │    profile   │    │                  │    │  - Notify     │  │
│  └──────────────┘    └──────────────────┘    └───────────────┘  │
│         │                                           │           │
│         │         Manual step (~biweekly)            │           │
│         ▼                                           ▼           │
│  ┌──────────────┐                           ┌───────────────┐  │
│  │  cookies.txt │                           │  wl.json      │  │
│  │  (Netscape)  │                           │  (structured) │  │
│  └──────────────┘                           └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Minimal Script

```bash
#!/bin/bash
# fetch-watch-later.sh
# Requires: pip install yt-playlist-export

COOKIE_FILE="$HOME/.config/youtube/cookies.txt"
OUTPUT_DIR="$HOME/dev/life/content/.scratchpad"
DATE=$(date +%Y-%m-%d)

yt-playlist-export \
  --cookies "$COOKIE_FILE" \
  -f json \
  -o "$OUTPUT_DIR/${DATE}-watch-later.json" \
  "https://www.youtube.com/playlist?list=WL"

echo "Exported Watch Later to $OUTPUT_DIR/${DATE}-watch-later.json"
```

---

## 10. Summary of Tools

| Tool | Type | WL Access | Output | Maintenance |
|------|------|-----------|--------|-------------|
| YouTube Data API v3 | Official API | **Blocked** | - | - |
| yt-dlp | CLI | Yes (cookies) | Text/JSON | Cookie refresh |
| yt-playlist-export | Python CLI | Yes (cookies) | JSON/CSV | Cookie refresh |
| Chrome console JS | Manual | Yes (logged in) | JSON | DOM selectors may change |
| yt-watchlater-exporter | Chrome ext | Yes (logged in) | JSON | DOM selectors may change |
| YT Watch Later Tool | Chrome ext | Yes (logged in) | CSV | Closed source |
| Google Takeout | Google service | Partial | HTML/JSON | Manual trigger |
| Playwright/Selenium | Automation | Yes (session) | Custom | DOM selectors + bot detection |

---

## Sources

- [YouTube Data API v3 Revision History (Sept 2016)](https://developers.google.com/youtube/v3/revision_history#september-15-2016)
- [yt-dlp Wiki: Exporting YouTube Cookies](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)
- [yt-dlp Issue #518: Cannot access private playlist](https://github.com/yt-dlp/yt-dlp/issues/518)
- [yt-dlp Issue #5203: Watch Later playlist broken](https://github.com/yt-dlp/yt-dlp/issues/5203)
- [yt-dlp Issue #11773: Automating YouTube cookie export](https://github.com/yt-dlp/yt-dlp/issues/11773)
- [MichaelCade/youtube-watch-later-mess](https://github.com/MichaelCade/youtube-watch-later-mess)
- [daydiff/yt-playlist-export](https://github.com/daydiff/yt-playlist-export)
- [afnan-nex/yt-watchlater-exporter](https://github.com/afnan-nex/yt-watchlater-exporter)
- [EposVox: Downloading Watch Later with yt-dlp](https://demodisc.zone/t/downloading-your-youtube-watch-later-playlist-with-yt-dlp/197)
- [StackOverflow: YouTube API Watch Later Playlist](https://stackoverflow.com/questions/41451533/youtube-api-getting-watch-later-playlist)
