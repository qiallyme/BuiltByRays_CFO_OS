# Frontmatter Improvements & Script Updates

## Overview
Updated the knowledge base scripts to prevent frontmatter duplication and ensure proper prefix preservation.

## Key Improvements

### 1. Enhanced Frontmatter Fix Script (`kb_fix_frontmatter.py`)
- **Duplicate Prevention**: Now removes multiple frontmatter blocks, keeping only the first
- **Prefix Preservation**: Better handling of A./B./C. prefixes in titles
- **Clean YAML**: Improved formatting with proper escaping and list handling
- **Deduplication**: Removes duplicate tags, aliases, and empty values

### 2. New NPM Scripts in `package.json`

```json
{
  "kb:clean": "python kb_cleanup_headers.py --base \"./content\" --apply",
  "kb:frontmatter": "python kb_fix_frontmatter.py --base \"./content\" --apply", 
  "kb:autotag": "python kb_autotag_backlink.py --base \"./content\" --apply",
  "kb:toc": "python kb_toc_and_tags.py --base \"./content\" --apply",
  "kb:rebuild": "npm run kb:clean && npm run kb:frontmatter && npm run kb:autotag && npm run kb:toc && npm run build",
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

### `kb:frontmatter` 
- Ensures single, clean frontmatter block
- Preserves A./B./C. prefixes in titles
- Properly formats tags and aliases
- Syncs H1 headers with frontmatter titles
- Removes duplicate entries

### `kb:autotag`
- Auto-generates tags based on content
- Creates backlinks between related files
- Updates existing tags intelligently

### `kb:toc`
- Generates table of contents for folders
- Updates global index
- Maintains navigation structure

## Benefits

1. **No More Duplicates**: Prevents multiple frontmatter blocks
2. **Prefix Preservation**: Maintains A./B./C. ordering in titles
3. **Clean YAML**: Proper formatting and escaping
4. **Modular Workflow**: Run individual steps or full rebuild
5. **Consistent Structure**: Standardized across all content

## Troubleshooting

If you encounter issues:
1. Run `npm run kb:clean` first to remove duplicates
2. Then run `npm run kb:frontmatter` to fix formatting
3. Use `npm run kb:rebuild` for a complete fresh build

The scripts are designed to be idempotent - running them multiple times won't cause issues.
