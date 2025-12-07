from selectolax.parser import HTMLParser, Node
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from backend.models import Section, Content, Link, Image


class SectionParser:
    NOISE_SELECTORS = [
        '[class*="cookie"]',
        '[class*="banner"]',
        '[class*="popup"]',
        '[class*="modal"]',
        '[class*="overlay"]',
        '[id*="cookie"]',
        '[id*="banner"]',
        '[id*="popup"]',
        '[id*="modal"]',
        '[id*="overlay"]',
        '[role="dialog"]',
        '[role="alertdialog"]',
    ]
    
    SECTION_TYPE_MAP = {
        "header": "nav",
        "nav": "nav",
        "footer": "footer",
        "main": "section",
        "article": "section",
        "section": "section",
    }
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.section_counter = 0
    
    def parse(self, html: str) -> List[Section]:
        """
        Parse HTML into sections
        Returns list of Section models
        """
        tree = HTMLParser(html)
        
        # Remove noise elements
        self._remove_noise(tree)
        
        # Extract sections using landmarks and headings
        sections = []
        
        # First, try to extract by semantic landmarks
        landmarks = tree.css("header, nav, main, section, article, footer")
        if landmarks:
            for landmark in landmarks:
                try:
                    section = self._extract_section(landmark)
                    if section and (section.content.text.strip() or section.content.headings):
                        sections.append(section)
                except Exception as e:
                    # Skip sections that fail to extract
                    continue
        
        # If no landmarks found, use heading-based grouping
        if not sections:
            try:
                sections = self._extract_by_headings(tree)
            except Exception:
                sections = []
        
        # Ensure at least one section - try body, then html, then create minimal section
        if not sections:
            body = tree.css_first("body")
            if body:
                try:
                    section = self._extract_section(body, default_type="section", default_label="Content")
                    if section:
                        sections.append(section)
                except Exception:
                    pass
            
            # If still no sections, try html element
            if not sections:
                html_elem = tree.css_first("html")
                if html_elem:
                    try:
                        section = self._extract_section(html_elem, default_type="section", default_label="Page Content")
                        if section:
                            sections.append(section)
                    except Exception:
                        pass
        
        # Final fallback - create a minimal section from the entire document
        if not sections:
            try:
                # Get all text from the body element
                body = tree.css_first("body")
                if body:
                    all_text = body.text()[:5000] if body.text() else ""
                else:
                    # Try to get text from html element
                    html_elem = tree.css_first("html")
                    all_text = html_elem.text()[:5000] if html_elem and html_elem.text() else ""
                
                if all_text.strip():
                    sections.append(Section(
                        id="fallback-0",
                        type="unknown",
                        label="Page Content",
                        sourceUrl=self.base_url,
                        content=Content(
                            text=all_text,
                            headings=[],
                            links=[],
                            images=[],
                            lists=[],
                            tables=[]
                        ),
                        rawHtml=html[:5000],
                        truncated=len(html) > 5000
                    ))
                else:
                    # Absolute fallback
                    sections.append(Section(
                        id="fallback-0",
                        type="unknown",
                        label="Content",
                        sourceUrl=self.base_url,
                        content=Content(
                            text="No content could be extracted from this page.",
                            headings=[],
                            links=[],
                            images=[],
                            lists=[],
                            tables=[]
                        ),
                        rawHtml=html[:1000] if html else "",
                        truncated=len(html) > 1000 if html else False
                    ))
            except Exception:
                # Absolute fallback
                sections.append(Section(
                    id="fallback-0",
                    type="unknown",
                    label="Content",
                    sourceUrl=self.base_url,
                    content=Content(
                        text="No content could be extracted from this page.",
                        headings=[],
                        links=[],
                        images=[],
                        lists=[],
                        tables=[]
                    ),
                    rawHtml=html[:1000] if html else "",
                    truncated=len(html) > 1000 if html else False
                ))
        
        return sections
    
    def _remove_noise(self, tree: HTMLParser):
        """Remove noise elements like cookie banners, popups, etc."""
        for selector in self.NOISE_SELECTORS:
            elements = tree.css(selector)
            for elem in elements:
                try:
                    elem.decompose()
                except:
                    pass
    
    def _extract_section(self, element: Node, default_type: str = "section", default_label: str = None) -> Optional[Section]:
        """Extract a single section from an element"""
        if not element:
            return None
        
        # Determine section type
        tag_name = element.tag.lower()
        section_type = self.SECTION_TYPE_MAP.get(tag_name, default_type)
        
        # Check for specific type indicators
        classes = element.attributes.get("class", "").lower()
        section_id = element.attributes.get("id", "").lower()
        
        if "hero" in classes or "hero" in section_id:
            section_type = "hero"
        elif "pricing" in classes or "pricing" in section_id:
            section_type = "pricing"
        elif "faq" in classes or "faq" in section_id or "faqs" in classes:
            section_type = "faq"
        elif "grid" in classes or "grid" in section_id:
            section_type = "grid"
        elif "list" in classes or "list" in section_id:
            section_type = "list"
        
        # Extract content
        content_dict = self._extract_content(element)
        content = Content(**content_dict)
        
        # Generate label
        label = default_label or self._generate_label(element, content_dict)
        
        # Generate ID
        section_id_val = element.attributes.get("id")
        if not section_id_val:
            section_id_val = f"{section_type}-{self.section_counter}"
            self.section_counter += 1
        else:
            section_id_val = f"{section_type}-{section_id_val}"
        
        # Get raw HTML (truncated)
        raw_html = element.html
        truncated = len(raw_html) > 5000
        if truncated:
            raw_html = raw_html[:5000] + "..."
        
        return Section(
            id=section_id_val,
            type=section_type,
            label=label,
            sourceUrl=self.base_url,
            content=content,
            rawHtml=raw_html,
            truncated=truncated
        )
    
    def _extract_content(self, element: Node) -> Dict:
        """Extract content from an element"""
        content = {
            "headings": [],
            "text": "",
            "links": [],
            "images": [],
            "lists": [],
            "tables": []
        }
        
        # Extract headings
        headings = element.css("h1, h2, h3, h4, h5, h6")
        content["headings"] = [h.text().strip() for h in headings if h.text().strip()]
        
        # Extract text (excluding script and style)
        text_parts = []
        for node in element.traverse():
            if node.tag in ("script", "style", "noscript"):
                continue
            if node.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                continue  # Already captured
            text = node.text(deep=False, separator=" ").strip()
            if text:
                text_parts.append(text)
        content["text"] = " ".join(text_parts)[:5000]  # Limit text length
        
        # Extract links
        links = element.css("a[href]")
        for link in links:
            href = link.attributes.get("href", "")
            if href:
                # Make absolute URL
                absolute_href = urljoin(self.base_url, href)
                text = link.text().strip()
                if not text:
                    # Try to get text from child nodes
                    text = link.text(deep=True).strip()[:100]
                if text or href:  # Include link even if no text
                    content["links"].append(Link(
                        text=str(text or href),
                        href=str(absolute_href)
                    ))
        
        # Extract images
        images = element.css("img")
        for img in images:
            src = img.attributes.get("src", "")
            if src:
                absolute_src = urljoin(self.base_url, src)
                # Get alt attribute, default to empty string if None or missing
                alt_attr = img.attributes.get("alt")
                alt = str(alt_attr) if alt_attr is not None else ""
                content["images"].append(Image(
                    src=str(absolute_src),
                    alt=alt
                ))
        
        # Extract lists
        lists = element.css("ul, ol")
        for list_elem in lists:
            items = list_elem.css("li")
            list_items = [item.text().strip() for item in items if item.text().strip()]
            if list_items:
                content["lists"].append(list_items)
        
        # Extract tables (basic structure)
        tables = element.css("table")
        for table in tables:
            table_data = {
                "rows": []
            }
            rows = table.css("tr")
            for row in rows:
                cells = row.css("td, th")
                row_data = [cell.text().strip() for cell in cells]
                if row_data:
                    table_data["rows"].append(row_data)
            if table_data["rows"]:
                content["tables"].append(table_data)
        
        return content
    
    def _generate_label(self, element: Node, content_dict: Dict) -> str:
        """Generate a label for a section"""
        # Try to use first heading
        if content_dict.get("headings"):
            return content_dict["headings"][0]
        
        # Try aria-label or data-label
        aria_label = element.attributes.get("aria-label")
        if aria_label:
            return aria_label
        
        data_label = element.attributes.get("data-label")
        if data_label:
            return data_label
        
        # Use first 5-7 words of text
        text = content_dict.get("text", "").strip()
        if text:
            words = text.split()[:7]
            label = " ".join(words)
            if len(label) > 50:
                label = label[:47] + "..."
            return label or "Section"
        
        # Fallback
        tag_name = element.tag.lower()
        return tag_name.capitalize() if tag_name else "Section"
    
    def _extract_by_headings(self, tree: HTMLParser) -> List[Section]:
        """Extract sections by grouping content under headings"""
        sections = []
        body = tree.css_first("body")
        if not body:
            return sections
        
        # Find all h1-h3 headings
        headings = body.css("h1, h2, h3")
        if not headings:
            return sections
        
        # Group content under each heading
        for heading in headings:
            # Get content following this heading until next heading
            section_content = []
            current = heading.next
            while current:
                if current.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    if current.tag <= heading.tag:  # Same or higher level heading
                        break
                section_content.append(current)
                current = current.next
            
            # Create a wrapper element for this section
            # For simplicity, we'll extract from the heading's parent or create a virtual section
            parent = heading.parent
            if parent:
                section = self._extract_section(parent, default_type="section")
                if section and section.content.text.strip():
                    sections.append(section)
        
        return sections

