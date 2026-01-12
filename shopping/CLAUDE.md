# Shopping

Lists and tracking for purchases and items to buy.

---

## Purpose

A place to track shopping lists, wishlists, and purchase planning. Simple and practical.

---

## Structure

```
shopping/
├── .scratchpad/           # Active shopping lists
│   └── .history/          # Archived lists
├── {date}-{category}.md   # Top-level lists (optional)
└── CLAUDE.md
```

---

## File Format

```markdown
# {Category} Shopping

**Date:** {M-DD-YY}
**Status:** [ ] Planning | [ ] Ready to Buy | [x] Purchased

---

## Items

- [ ] Item 1 — notes, size, link
- [ ] Item 2
- [x] Item 3 (purchased)

## Notes
- Budget considerations, store preferences, etc.
```

---

## Guidelines

- One list per category or shopping trip
- Check off items as purchased
- Archive completed lists to `.history/`
- Link to products when helpful
