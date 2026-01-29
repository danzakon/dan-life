# Take-Home Option B: Data Pipeline Agent

## Overview

Build an intelligent data understanding tool that classifies, describes, and organizes CSV data through AI-powered analysis.

---

## The Product

You're building **DataForge**, an intelligent data understanding tool. Users upload CSV files, and the system automatically classifies what the data is, generates descriptions, and suggests how to organize and clean it.

The magic is in the AI: given any CSV, the system should figure out what it's looking at and help the user make sense of it.

### Core User Flow

**1. UPLOAD**

User uploads "mystery_data.csv". System shows upload progress. Processing happens asynchronously.

**2. CLASSIFY & DESCRIBE**

System analyzes and determines what the data is:

> "This appears to be e-commerce transaction data with 12,847 orders from 2023-2024. Key columns include customer_id, order_date, product_sku, and total_amount. Data quality: 3 issues detected."

Generates a data dictionary with inferred column meanings.

**3. ORGANIZE & SUGGEST**

System recommends:
- Rename 'col1' → 'customer_id'
- Standardize date format in 'order_date'
- Normalize 'status' values (5 variations → 3)
- Split 'full_name' into 'first_name' + 'last_name'

User accepts/rejects each suggestion.

**4. EXPLORE & TRANSFORM**

Apply additional transformations via natural language. Preview changes before applying. Full transformation history with undo.

**5. EXPORT**

Download cleaned data. View transformation history.

---

## What You're Building

### Frontend

A dashboard web application with:

1. **Upload Interface**
   - Drag-and-drop or file picker
   - Progress indicator for uploads
   - Support for multiple file uploads (queued or parallel)
   - Clear status for each file: uploading → processing → ready → error

2. **Classification & Description Panel**
   - AI-generated description of what the data is
   - Data dictionary showing each column with:
     - Inferred name/meaning
     - Detected type (string, number, date, boolean, categorical)
     - Statistics (nulls, unique values, distribution)
   - Data quality summary (issues detected)

3. **Organization Suggestions**
   - List of AI-recommended changes
   - Accept/reject each suggestion individually
   - Preview what the change would look like
   - Explanation of why each change is suggested

4. **Data Explorer**
   - Paginated data table
   - Search/filter capabilities
   - Column sorting

5. **Transformation Panel**
   - Natural language input for additional transformations
   - Transformation history with undo capability
   - Clear indication of pending vs. applied changes

6. **File Management**
   - List of uploaded files with status
   - Switch between files
   - Delete files

7. **Export Interface**
   - Download transformed data as CSV
   - View complete transformation history

### Backend

1. **File Handling**
   - Accept CSV uploads
   - Store files persistently
   - Handle large files asynchronously (don't block)
   - Status polling or websocket for progress updates

2. **AI Analysis Pipeline**
   - Classify what kind of data this is
   - Generate natural language description
   - Infer column meanings and suggest names
   - Detect data quality issues
   - Generate organization suggestions

3. **Organization Engine**
   - Apply accepted suggestions
   - Track all transformations
   - Support undo/rollback
   - Preserve original data (non-destructive)

4. **Data API**
   - Paginated data retrieval
   - Column statistics
   - Transformation application

---

## What "Organization" Means

The system should suggest concrete ways to clean up and standardize the data:

### Column Organization

| Before | Suggested | Reason |
|--------|-----------|--------|
| `col1`, `col2`, `col3` | `customer_id`, `order_date`, `total` | Infer meaningful names from content |
| `firstName`, `first_name`, `FIRSTNAME` | `first_name` | Standardize naming convention |
| `full_name` | `first_name`, `last_name` | Split compound columns |
| `addr1`, `addr2`, `city`, `zip` | Grouped as "Address fields" | Identify related columns |
| Columns in random order | ID columns first, then data, then timestamps | Logical column ordering |

### Value Normalization

| Before | Suggested | Reason |
|--------|-----------|--------|
| `"USA"`, `"US"`, `"United States"`, `"usa"` | `"US"` | Standardize categorical values |
| `"2024-01-15"`, `"Jan 15, 2024"`, `"1/15/24"` | `"2024-01-15"` | Normalize date formats |
| `"$1,234.56"`, `"1234.56"`, `"1,234.56"` | `1234.56` (numeric) | Clean currency formatting, convert type |
| `"  John Smith  "`, `"JOHN SMITH"` | `"John Smith"` | Trim whitespace, normalize casing |
| `"N/A"`, `"null"`, `""`, `"-"` | `null` | Standardize null representations |

### Structural Suggestions

The AI should surface insights like:
- "Column `order_id` appears to be a unique identifier (primary key)"
- "Columns `created_at` and `updated_at` should be datetime type"
- "Column `legacy_field` is 98% null—consider dropping"
- "Found 847 duplicate rows based on `order_id`"
- "Columns `price` and `quantity` could derive a `total` column"
- "Recommend sorting by `date` ascending for time-series analysis"

### Example Classification Output

**Dataset Classification:** E-Commerce Orders

**Description:**

This dataset contains 12,847 e-commerce transactions from an online retail store, spanning January 2023 to December 2024. Each row represents a single order with customer information, product details, and payment data.

**Data Dictionary:**

| Column | Type | Inferred Meaning |
|--------|------|------------------|
| col1 | string | → Rename to 'order_id' (unique) |
| col2 | string | → Rename to 'customer_email' |
| col3 | mixed dates | → Rename to 'order_date', fix format |
| col4 | string | → Rename to 'product_name' |
| col5 | currency str | → Rename to 'amount', convert to numeric |
| col6 | categorical | → Rename to 'status' (5→3 values) |

**Data Quality Issues:**

- 234 rows (1.8%) have null customer_email
- Date format inconsistent in col3 (3 different formats detected)
- col5 has currency symbols mixed with plain numbers
- 5 distinct values for status, but "shipped" and "Shipped" are duplicates
- 12 duplicate order_ids detected

**Suggested Actions:**

1. Rename columns to meaningful names (6 changes)
2. Standardize date format to ISO-8601 (affects 4,521 rows)
3. Convert amount to numeric, remove currency symbols (affects 12,847 rows)
4. Normalize status values: "shipped"/"Shipped" → "shipped" (affects 203 rows)
5. Flag or remove duplicate order_ids (affects 12 rows)

---

## System Constraints: Robustness

Your dashboard will be tested for robustness. Consider:

### Upload Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| Single file upload | Works smoothly |
| Bulk upload (5+ files at once) | Queued or parallel processing, clear status for each |
| Large files (50MB+) | Async processing, progress feedback, no UI freeze |
| User navigates away mid-upload | Upload continues or gracefully cancels |
| Invalid file (not CSV, empty, corrupted) | Clear error message, doesn't crash |

### State & Persistence

| Scenario | Expected Behavior |
|----------|-------------------|
| Page refresh during processing | Processing continues, state preserved |
| Page refresh after upload | Files and transformations still there |
| Multiple browser tabs | Consistent state or clear handling |
| Come back hours later | Session/data persisted |

### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| CSV with 1 row | Handles gracefully (limited stats) |
| CSV with 500 columns | Doesn't freeze, scrollable UI |
| CSV with 100k+ rows | Paginated, performant |
| Unicode/special characters | Displays correctly |
| Inconsistent row lengths | Detected and surfaced |
| Extremely long cell values | Truncated in display, preserved in data |

### Concurrent Operations

| Scenario | Expected Behavior |
|----------|-------------------|
| Upload while another file processing | Both tracked independently |
| Apply transformation during upload | Queued or handled gracefully |
| Rapid undo/redo clicks | Consistent state |

---

## Test Data

**You are responsible for creating your own test data.**

Create diverse test files that demonstrate your system handles:

- **Different domains**: sales data, user records, server logs, inventory, survey responses
- **Different sizes**: 100 rows, 10k rows, 100k+ rows
- **Different messiness levels**: clean, moderate issues, very messy
- **Different structures**: few columns, many columns, nested-looking data

**We will test your submission with our own datasets that you haven't seen.** Your system should handle any well-formed CSV gracefully and provide useful classification/organization for most common data types.

**Include in your README:**
- How to generate or obtain your test data
- What test scenarios you've validated
- Known limitations (e.g., "classification works best for transactional data")
- Largest file size you've tested successfully

---

## What We're NOT Specifying

These are intentional decisions for you to make:

- Tech stack (use whatever you're productive in)
- How you handle large files (streaming, chunking, workers, etc.)
- Storage approach (database, file system, in-memory, etc.)
- How the AI performs classification and generates suggestions
- Whether suggestions are generated eagerly or on-demand
- Visual design (functional > pretty, but should be usable)

---

## Deliverables

### 1. Hosted Application

Deploy your application somewhere accessible:
- Vercel, Railway, Render, Fly.io, or similar
- Should be functional for us to test with our own CSV files
- Note any file size limitations of your deployment

### 2. Source Code

- GitHub repo (can be private, invite us)
- Include a README with:
  - How to run locally
  - Environment variables needed
  - Test data generation instructions
  - Performance notes (largest file tested)
  - Known limitations

### 3. Loom Video (15-20 minutes)

Record yourself covering:

**Part 1: Demo (5-7 min)**
- Upload a file and show the classification/description
- Walk through the organization suggestions
- Accept some suggestions, reject others
- Apply a natural language transformation
- Show undo/history
- Upload a second file while first is still in view
- Show what happens with a problematic file

**Part 2: Architecture (5-7 min)**
- Tech stack choices and why
- How the AI classification/suggestion pipeline works
- How you handle large files and async processing
- State management approach
- Storage decisions

**Part 3: Decisions & Tradeoffs (5-7 min)**
- Hardest design decisions
- What you'd do differently with more time
- Where you used AI assistance and where you didn't
- What would break first at scale
- How you'd extend this to other file formats

---

## Time Expectation

We expect this to take **4-6 hours** for a working solution. You can spend more if you're enjoying it, but we'd rather see a solid core experience than extensive features.

**What "done" looks like:**
- Upload → Classify → Describe → Suggest → Export flow works
- AI classification produces useful output for common data types
- Organization suggestions are sensible and actionable
- Handles a 10k row file without issues
- Robustness basics covered (refresh doesn't lose state, errors handled)
- Clear explanation of how you'd scale to larger files

---

## Evaluation Criteria

| Dimension | Weight | What We're Looking For |
|-----------|--------|------------------------|
| **AI Quality** | 25% | Are classifications accurate? Are suggestions useful? |
| **System Design** | 25% | How do you handle async, large files, state, persistence? |
| **Product Thinking** | 25% | Is the UX coherent? Errors handled? Progress clear? |
| **Communication** | 25% | Can you explain decisions? Understand tradeoffs? |

---

## Questions?

If anything is genuinely unclear, email us. We're happy to clarify requirements but won't give hints on design decisions—those are part of what we're evaluating.

---

## Internal Evaluation Notes

*This section is for internal use only—not shared with candidates.*

### What This Tests

**Primary signals:**
- AI/LLM integration (classification, description, suggestions)
- System design (async processing, file handling, state)
- Data intuition (do they understand what good organization looks like?)
- Product sense (is the UX coherent? error handling?)

**Hidden complexity:**
- Classification requires actual understanding, not just pattern matching
- Suggestion quality varies wildly based on prompting strategy
- Large file handling is non-trivial
- Undo with AI-generated changes is tricky
- Balancing eager vs. lazy computation

### Red Flags

| Red Flag | What It Suggests |
|----------|------------------|
| Classification is generic/useless | Didn't invest in AI quality |
| Suggestions are obvious/shallow | Surface-level implementation |
| Can't handle 10k rows | Didn't think about scale |
| Refresh loses everything | Missed persistence requirement |
| Can't explain how AI works | Delegated entirely to Claude |
| No error handling | Didn't test edge cases |

### Follow-Up Questions (For Live Call)

- "Walk me through how your classification prompt works."
- "What if a user uploads a 1GB file? Walk me through what happens."
- "How would you handle a CSV where the AI misclassifies the data?"
- "What if two columns have the same inferred name?"
- "How would you add support for Excel files?"
- "The AI suggested dropping a column that's actually important. How do you mitigate that?"
- "How would you make the suggestions improve over time based on user feedback?"
