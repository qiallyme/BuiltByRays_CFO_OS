# Frontmatter Improvements & Script Updates

## Overview
Updated the knowledge base scripts to prevent frontmatter duplication, ensure proper prefix preservation, implement sentence case formatting, and fix duplicate H1 headings that cause Quartz to show titles twice.

## Key Improvements

### 1. Enhanced Frontmatter Fix Script (`kb_fix_frontmatter.py`)
- **Aggressive Duplicate Prevention**: Now removes ALL duplicate frontmatter blocks, keeping only the first
- **Prefix Preservation**: Better handling of A./B./C. prefixes in titles
- **Clean YAML**: Improved formatting with proper escaping and list handling
- **Deduplication**: Removes duplicate tags, aliases, and empty values
- **Title Validation**: Never allows "index" as a title - always derives proper title from filename or H1
- **Sentence Case Formatting**: Converts all titles to proper sentence case while preserving prefixes

### 2. Enhanced Cleanup Script (`kb_cleanup_headers.py`)
- **More Aggressive Duplicate Removal**: Improved handling of consecutive frontmatter blocks
- **Title Protection**: Prevents "index" titles from being created
- **Sentence Case Support**: Converts titles to sentence case format

### 3. New Duplicate H1 Fix Script (`kb_fix_duplicate_h1.py`)
- **Prevents Quartz Duplicate Titles**: Removes H1 headings that match frontmatter titles
- **Smart Matching**: Normalizes titles for comparison (handles quotes, spacing, case)
- **Preserves Content**: Only removes the first matching H1, keeps all other headings
- **Bulk Processing**: Automatically fixes all files with duplicate H1 issues

### 4. New NPM Scripts in `package.json`

```json
{
  "kb:clean": "python kb_cleanup_headers.py --base \"./content\" --apply",
  "kb:frontmatter": "python kb_fix_frontmatter.py --base \"./content\" --apply", 
  "kb:duplicate-h1": "python kb_fix_duplicate_h1.py --base \"./content\" --apply",
  "kb:autotag": "python kb_autotag_backlink.py --base \"./content\" --apply",
  "kb:toc": "python kb_toc_and_tags.py --base \"./content\" --apply",
  "kb:rebuild": "npm run kb:clean && npm run kb:frontmatter && npm run kb:duplicate-h1 && npm run kb:autotag && npm run kb:frontmatter && npm run kb:toc && npm run kb:frontmatter && npm run build",
  "kb:preview": "npm run kb:rebuild && npx serve public -l 8080"
}
```

## Usage

### Individual Scripts
```bash
# Clean up headers and remove duplicates
npm run kb:clean

# Fix frontmatter formatting and preserve prefixes  
npm run kb:frontmatter

# Remove duplicate H1 headings that match frontmatter titles
npm run kb:duplicate-h1

# Auto-tag and create backlinks
npm run kb:autotag

# Generate TOCs and global index
npm run kb:toc
```

### Full Rebuild
```bash
# Complete rebuild with all steps
npm run kb:rebuild

# Rebuild and preview
npm run kb:preview
```

## What Each Script Does

### `kb:clean`
- Removes duplicate frontmatter blocks
- Lifts loose key:value lines into proper YAML
- Strips injected blocks for clean re-insertion
- Deduplicates repeated H1 headers
- Prevents "index" titles
- Converts titles to sentence case

### `kb:frontmatter` 
- Ensures single, clean frontmatter block
- Preserves A./B./C. prefixes in titles
- Properly formats tags and aliases
- Syncs H1 headers with frontmatter titles
- Removes duplicate entries
- **Aggressively removes ALL duplicate frontmatter blocks**
- **Never allows "index" as title**
- **Converts all titles to sentence case**

### `kb:duplicate-h1`
- **Prevents Quartz from showing duplicate titles**
- Removes H1 headings that match frontmatter titles exactly
- Normalizes titles for smart matching (handles quotes, spacing, case)
- Only removes the first matching H1, preserves all other content
- **Essential for clean Quartz rendering**

### `kb:autotag`
- Auto-generates tags based on content
- Creates backlinks between related files
- Updates existing tags intelligently

### `kb:toc`
- Generates table of contents for folders
- Updates global index
- Maintains navigation structure

## Enhanced Workflow

The rebuild process now includes multiple frontmatter fix passes:
1. **Initial cleanup** - Remove duplicates
2. **Post-cleanup fix** - Ensure proper formatting
3. **Duplicate H1 fix** - Remove H1s that match frontmatter titles
4. **Post-autotag fix** - Clean up after tag generation
5. **Post-TOC fix** - Clean up after TOC generation
6. **Final fix** - Last cleanup pass

This ensures that even if other scripts add duplicate frontmatter, it gets cleaned up at each step.

## Sentence Case Formatting

The system now automatically converts titles to sentence case:
- **Before**: "A. YOUR DETAILS" or "A. Your Details"
- **After**: "A. Your Details"

The sentence case function:
- Preserves A./B./C. prefixes exactly as they are
- Converts the rest of the title to sentence case
- Handles special cases like acronyms and proper nouns
- Maintains proper spacing and formatting

## Duplicate H1 Problem & Solution

### The Problem
Quartz renders the frontmatter title as the page title. If there's also an H1 in the body that matches the frontmatter title, you see the title twice:
- **Frontmatter title**: "00 Proposal" (rendered by Quartz)
- **Body H1**: "# 00 Proposal" (rendered in content)
- **Result**: Duplicate "00 Proposal" on the page

### The Solution
The `kb:duplicate-h1` script automatically:
- Compares frontmatter titles with H1 headings
- Removes H1s that match frontmatter titles exactly
- Preserves all other content and headings
- Normalizes titles for smart matching

### Example Fix
**Before:**
```yaml
---
title: "00 Proposal"
---
# 00 Proposal
## Content here...
```

**After:**
```yaml
---
title: "00 Proposal"
---
## Content here...
```

## Complete Solution for Duplicate Index Issues

### The Problem
When you see "00 Proposal" twice on a page, it's typically because:
1. **Frontmatter title** is rendered by Quartz as the page title
2. **Body H1** also contains "# 00 Proposal" 
3. **Result**: Duplicate title display

### The Complete Fix
1. **Delete duplicate files**: Remove any root `content/00_proposal.md` if you have `content/00_proposal/index.md`
2. **Clean frontmatter**: Use proper YAML format with all necessary fields
3. **Remove duplicate H1**: Delete the first H1 if it matches the frontmatter title
4. **Start content with H2**: Begin your content with `##` headings instead of `#`

### Example of Proper Structure
```yaml
---
title: "00 Proposal"
description: "Executive Growth Partnership Proposal overview."
permalink: /00-proposal/
tags:
  - proposal
  - engagement
  - scope
lang: en
publish: true
draft: false
enableToc: true
aliases:
  - "Proposal"
  - "00_proposal"
created: 2025-08-15
updated: 2025-08-15
---

## BuiltByRays™ Executive Growth Partnership Proposal

[Content starts here with H2 headings...]
```

## Benefits

1. **No More Duplicates**: Prevents multiple frontmatter blocks completely
2. **Prefix Preservation**: Maintains A./B./C. ordering in titles
3. **Clean YAML**: Proper formatting and escaping
4. **Modular Workflow**: Run individual steps or full rebuild
5. **Consistent Structure**: Standardized across all content
6. **Robust Process**: Multiple cleanup passes prevent re-introduction of duplicates
7. **Proper Titles**: Never allows "index" as a title
8. **Sentence Case**: Consistent, professional title formatting
9. **Clean Quartz Rendering**: No duplicate titles on pages
10. **Smart H1 Management**: Automatic removal of redundant headings
11. **Complete Solution**: Handles all aspects of duplicate title issues

## Troubleshooting

If you encounter issues:
1. Run `npm run kb:clean` first to remove duplicates
2. Then run `npm run kb:frontmatter` to fix formatting
3. Run `npm run kb:duplicate-h1` to fix duplicate titles
4. Use `npm run kb:rebuild` for a complete fresh build with multiple cleanup passes

The scripts are designed to be idempotent - running them multiple times won't cause issues.

## Recent Fixes

- **Aggressive duplicate removal**: Scripts now remove ALL duplicate frontmatter blocks
- **Title validation**: Never allows "index" as a title
- **Multiple cleanup passes**: Frontmatter is cleaned after each processing step
- **Enhanced regex patterns**: Better detection and removal of duplicate blocks
- **Sentence case formatting**: All titles converted to proper sentence case
- **Prefix preservation**: A./B./C. prefixes maintained exactly as specified
- **Duplicate H1 fix**: New script prevents Quartz from showing duplicate titles
- **Smart title matching**: Normalizes titles for accurate duplicate detection
- **Complete workflow**: All scripts work together to prevent re-introduction of issues
