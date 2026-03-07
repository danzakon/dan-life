---
name: db-rebuild
description: Reconstruct index.db from content file frontmatter. Use when the database
  is corrupted, lost, or needs to be rebuilt from scratch.
argument-hint: ""
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# DB Rebuild

Safety net for the SQLite index. Scans all content files for frontmatter `id` fields and reconstructs `content/pipeline/index.db` from scratch. The markdown files are the ground truth; the database is a derived index.

---

## Trigger

- "Rebuild the database"
- "db:rebuild"
- When `index.db` is missing, corrupted, or returns unexpected results

---

## Process

### Step 1: Back up existing DB (if it exists)

```bash
cp content/pipeline/index.db content/pipeline/index.db.bak 2>/dev/null || true
```

### Step 2: Recreate from schema

```bash
rm -f content/pipeline/index.db
sqlite3 content/pipeline/index.db < content/pipeline/schema.sql
```

### Step 3: Scan raw files

Glob all files in `content/raw/`:

```
content/raw/x-posts/*.md
content/raw/x-articles/*.md
content/raw/youtube/*.md
content/raw/web/*.md
```

For each file, read the YAML frontmatter and extract:
- `id` (required — skip files without an id)
- `source-type`
- `ingest-source`
- `original-url`
- `captured` → `created_at`

Insert into items table with `status = 'raw'`.

### Step 4: Scan briefs

Glob `content/briefs/*.md`. For each file:
- Read frontmatter: `id`, `format`, `platform`, `series-id`, `status`
- Update the matching item's `brief_file` and `status` to at least `approved`

### Step 5: Scan post files

Glob `content/posts/*.md`. Search for `content-id:` fields in each post entry.
- For each content-id found, update the item's `draft_file` and set `status` to at least `draft`

### Step 6: Scan article drafts

Glob `content/articles/drafts/*.md`. Read frontmatter for `content-id` field.
- Update `draft_file` and `status` accordingly.

### Step 7: Scan published articles

Glob `content/articles/published/*.md`.
- If a `content-id` exists, set `status = 'published'`

### Step 8: Scan research reports

Glob `research/reports/*.md`. For each file with an `id` frontmatter field:
- Insert into items with `source_type = 'research'`, `ingest_source = 'research'`

### Step 9: Rebuild series table

Read `content/pipeline/series.md`. Parse each series entry (id, title, theme, status) and insert into the `series` table.

### Step 10: Rebuild inbox index

Read all `content/inbox/YYYY-MM-DD.md` files. For each item entry found (by `[ID]` pattern in headers), cross-reference against the items table and update status if the inbox shows a more advanced status.

### Step 11: Report

```
DB Rebuild Complete
─────────────────────────────────
  Items recovered:    47
  Briefs linked:      12
  Drafts linked:       8
  Published found:     3
  Research linked:     6
  Series rebuilt:      2

  Files without ID (skipped): 3
    content/raw/x-posts/some-old-file.md
    ...

  Status distribution:
    raw:        18
    inbox:       7
    approved:    5
    draft:       8
    refined:     3
    queued:      3
    published:   3

  Backup saved: content/pipeline/index.db.bak
```

---

## When to Use

- `index.db` is deleted or corrupted
- After manual edits to content files that may have changed IDs
- As a periodic integrity check (run and compare counts to live DB)
- After merging branches that may have conflicting DB states

---

## Prerequisites

`sqlite3` (pre-installed on macOS).
