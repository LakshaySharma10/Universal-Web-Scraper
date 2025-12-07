# Design Notes

## Static vs JS Fallback

**Strategy**: The scraper attempts static scraping first using httpx and selectolax. It then evaluates whether the static HTML is sufficient using a heuristic:

1. **Framework Detection**: Checks for React, Vue, or Angular in script tags
2. **Content Length**: If a JS framework is detected and text content is < 500 characters, it likely needs JS rendering
3. **Text Threshold**: If text content > 1000 characters, static is likely sufficient

If static scraping appears insufficient (based on the heuristic) or fails, the system automatically falls back to Playwright for JavaScript rendering.

## Wait Strategy for JS

- [x] Network idle : Waits for `networkidle` state (up to 10 seconds)
- [x] Fixed Delay: Adds a 1-second delay after initial load
- [x] Wait for selectors:  Wait for common content selectors (`main`, `article`, `body`, `[role='main']`) with 2-second timeout each


## Click & Scroll Strategy

**Click flows implemented:**
- **Tabs**: Detects and clicks `[role="tab"]` elements, tab buttons with `aria-controls`, and elements with `.tab` class
- **Load More**: Searches for buttons containing "Load more", "Show more", "See more" text, or elements with `load-more`/`show-more` in class/id
- **Pagination**: Follows "Next" links and `[rel="next"]` elements

**Scroll / pagination approach:**
- Performs scroll operations to reach depth ≥ 3
- Scrolls to bottom of page and waits 2 seconds for content to load
- Tracks scroll height to detect when new content loads
- Stops if no new content appears after 2 consecutive scrolls
- Follows pagination links when detected, resetting scroll count for new pages

**Stop conditions:**
- Maximum depth of 3 pages/scrolls reached
- No new content detected after 2 scrolls
- Timeout (30 seconds for page load, 2 seconds for interactions)

## Section Grouping & Labels

**Group DOM into sections:**
1. **Semantic Landmarks**: First attempts to extract sections from semantic HTML elements (`header`, `nav`, `main`, `section`, `article`, `footer`)
2. **Heading-Based**: If no landmarks found, groups content under headings (h1-h3) and their following content
3. **Fallback**: If neither method works, creates a single section from the `body` element

**Derive section `type` and `label`:**
- **Type Detection**:
  - Uses semantic HTML tags (header→nav, nav→nav, footer→footer, etc.)
  - Checks class/id for keywords: "hero"→hero, "pricing"→pricing, "faq"→faq, "grid"→grid, "list"→list
  - Defaults to "section" or "unknown" if no match
- **Label Generation**:
  1. Uses first heading (h1-h6) in the section
  2. Falls back to `aria-label` or `data-label` attributes
  3. Uses first 5-7 words of section text
  4. Final fallback: tag name capitalized

## Noise Filtering & Truncation

**Filtering out:**
- Cookie banners: `[class*="cookie"]`, `[id*="cookie"]`
- Popups/modals: `[class*="popup"]`, `[class*="modal"]`, `[id*="popup"]`, `[id*="modal"]`
- Overlays: `[class*="overlay"]`, `[id*="overlay"]`
- Dialogs: `[role="dialog"]`, `[role="alertdialog"]`
- Banners: `[class*="banner"]`, `[id*="banner"]`

These elements are removed from the DOM before section parsing to ensure clean content extraction.

**Truncate `rawHtml` and set `truncated`:**
- **Truncation Limit**: 5000 characters
- **Method**: If HTML exceeds 5000 chars, truncate and append "..."
- **Flag**: Set `truncated: true` if truncated, `false` otherwise

## Error Handling

Errors are collected throughout the scraping process and included in the response:
- **Validation Errors**: Invalid URL schemes, malformed URLs
- **Fetch Errors**: Network failures, timeouts, HTTP errors
- **Render Errors**: Playwright failures, browser crashes
- **Parse Errors**: HTML parsing failures, section extraction issues

All errors include a `message` and `phase` (validation, fetch, render, parse) for debugging.