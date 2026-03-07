-- Content Pipeline Index Schema
-- Source of truth for index.db structure.
-- Update this file when the schema changes and add a migration to migrations/.
--
-- v1: initial schema (2026-03-07)

CREATE TABLE IF NOT EXISTS items (
  id              TEXT PRIMARY KEY,   -- e.g., 20260307-BM-001
  created_at      TEXT NOT NULL,      -- ISO 8601 UTC
  source_type     TEXT,               -- x-post | x-article | youtube | web | research | thought
  ingest_source   TEXT,               -- bookmark-mining | x-account-monitor | reply-monitor | youtube-monitor | save-raw | idea-dump | research
  status          TEXT NOT NULL DEFAULT 'raw',
                                      -- raw → inbox → approved → brief → draft → refined → queued → published
  current_title   TEXT,               -- mutable; reflects latest working title
  original_url    TEXT,               -- link to the source content
  raw_file        TEXT,               -- relative path from repo root to raw content file
  brief_file      TEXT,               -- relative path to brief file (if exists)
  draft_file      TEXT,               -- relative path + optional #anchor for items in weekly files
  series_id       TEXT,               -- FK to series.id (nullable)
  platform        TEXT,               -- Twitter | LinkedIn | Both
  format          TEXT,               -- post | thread | article | post+article
  published_at    TEXT,               -- ISO 8601 UTC when published
  multiplier      TEXT,               -- single | full-tree (scope of what was generated)
  notes           TEXT                -- freeform notes from interview or review
);

CREATE TABLE IF NOT EXISTS series (
  id       TEXT PRIMARY KEY,          -- slug, e.g., the-refinement-era
  title    TEXT NOT NULL,
  theme    TEXT,
  status   TEXT NOT NULL DEFAULT 'seeding'
                                      -- seeding | active | paused | complete
);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_created ON items(created_at);
CREATE INDEX IF NOT EXISTS idx_items_series ON items(series_id);
CREATE INDEX IF NOT EXISTS idx_items_ingest_source ON items(ingest_source);
