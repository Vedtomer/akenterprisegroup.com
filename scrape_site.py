#!/usr/bin/env python3
"""
Scraper for sunilmerchandising.com
Extracts: all pages, navigation, content, images, contact info
"""

import urllib.request
import urllib.error
import ssl
import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.sunilmerchandising.com"

# SSL context that ignores certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    """Fetch URL content ignoring SSL errors"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            return response.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return None

class ContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.nav_links = []
        self.images = []
        self.text_blocks = []
        self.headings = []
        self.in_nav = False
        self.in_heading = False
        self.in_p = False
        self.current_tag = None
        self.nav_depth = 0
        self._current_text = []
        self._skip_tags = {'script', 'style', 'noscript', 'head'}
        self._in_skip = False
        self._skip_depth = 0
        self.current_heading_tag = None
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Track skip tags
        if tag in self._skip_tags:
            self._in_skip = True
            self._skip_depth += 1
            return

        if self._in_skip:
            return

        # Meta tags
        if tag == 'meta':
            name = attrs_dict.get('name', attrs_dict.get('property', ''))
            content = attrs_dict.get('content', '')
            if name and content:
                self.meta[name] = content

        # Nav tracking
        if tag == 'nav':
            self.in_nav = True
            self.nav_depth = 1

        # Links
        if tag == 'a':
            href = attrs_dict.get('href', '')
            text_marker = f'__LINK_START_{len(self.links)}__'
            self.links.append({'href': href, 'text': '', '_marker': text_marker})
            if self.in_nav:
                self.nav_links.append({'href': href, 'text': '', '_idx': len(self.links)-1})

        # Images
        if tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            if src:
                self.images.append({'src': urljoin(BASE_URL, src), 'alt': alt})

        # Headings
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self.in_heading = True
            self.current_heading_tag = tag
            self._current_text = []

        # Paragraphs
        if tag == 'p':
            self.in_p = True
            self._current_text = []

        self.current_tag = tag

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip_depth -= 1
            if self._skip_depth <= 0:
                self._in_skip = False
                self._skip_depth = 0
            return

        if self._in_skip:
            return

        if tag == 'nav':
            self.in_nav = False
            self.nav_depth = 0

        if tag in ('h1', 'h2', 'h3', 'h4') and self.in_heading:
            text = ' '.join(self._current_text).strip()
            if text:
                self.headings.append({'tag': self.current_heading_tag, 'text': text})
            self.in_heading = False
            self._current_text = []

        if tag == 'p' and self.in_p:
            text = ' '.join(self._current_text).strip()
            if text and len(text) > 20:
                self.text_blocks.append(text)
            self.in_p = False
            self._current_text = []

    def handle_data(self, data):
        if self._in_skip:
            return
        text = data.strip()
        if text:
            if self.in_heading or self.in_p:
                self._current_text.append(text)

def extract_links_from_html(html, base_url):
    """Extract all internal links from HTML"""
    pattern = r'href=["\']([^"\']+)["\']'
    links = re.findall(pattern, html)
    internal = set()
    for link in links:
        if link.startswith('/') or base_url in link:
            full = urljoin(base_url, link)
            parsed = urlparse(full)
            if parsed.netloc in urlparse(base_url).netloc or parsed.netloc == '':
                # Remove anchors
                clean = full.split('#')[0].rstrip('/')
                if clean and clean != base_url.rstrip('/'):
                    internal.add(clean)
    return internal

def extract_nav_links(html, base_url):
    """Extract navigation menu links with their labels"""
    nav_pattern = r'<nav[^>]*>(.*?)</nav>'
    nav_match = re.search(nav_pattern, html, re.DOTALL | re.IGNORECASE)
    if not nav_match:
        # Try header
        nav_pattern = r'<header[^>]*>(.*?)</header>'
        nav_match = re.search(nav_pattern, html, re.DOTALL | re.IGNORECASE)

    nav_links = []
    if nav_match:
        nav_html = nav_match.group(1)
        link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
        for match in re.finditer(link_pattern, nav_html, re.DOTALL):
            href = match.group(1).strip()
            text = re.sub(r'\s+', ' ', match.group(2)).strip()
            if text and href:
                nav_links.append({'label': text, 'href': urljoin(base_url, href)})
    return nav_links

def extract_headings(html):
    """Extract all headings"""
    headings = []
    for tag in ['h1', 'h2', 'h3']:
        pattern = f'<{tag}[^>]*>(.*?)</{tag}>'
        for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                headings.append({'tag': tag, 'text': text})
    return headings

def extract_paragraphs(html):
    """Extract paragraph text"""
    paragraphs = []
    pattern = r'<p[^>]*>(.*?)</p>'
    for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
        text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 30:
            paragraphs.append(text)
    return paragraphs[:20]  # First 20 paragraphs

def extract_images(html, base_url):
    """Extract all images"""
    images = []
    pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*/?>'
    for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
        src = urljoin(base_url, match.group(1))
        alt = match.group(2) or ''
        images.append({'src': src, 'alt': alt})
    return images

def extract_contact_info(html):
    """Extract phone, email, address from HTML"""
    info = {}
    # Phone
    phone_match = re.search(r'(?:tel:|phone|ph|mobile)[:\s]*([+\d\s\-()]{8,20})', html, re.IGNORECASE)
    if phone_match:
        info['phone'] = phone_match.group(1).strip()
    # Also find phone numbers directly
    phones = re.findall(r'\+?[\d\s\-()]{10,18}', html)
    if phones:
        info['phones_found'] = list(set([p.strip() for p in phones[:5]]))

    # Email
    emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', html)
    if emails:
        info['emails'] = list(set(emails[:5]))

    # Address patterns
    addr_match = re.search(r'(?:address|location|addr)[:\s]*([^<]{20,100})', html, re.IGNORECASE)
    if addr_match:
        info['address_hint'] = addr_match.group(1).strip()

    return info

def extract_metadata(html):
    """Extract meta title, description, keywords"""
    meta = {}
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    if title_match:
        meta['title'] = re.sub(r'\s+', ' ', title_match.group(1)).strip()

    for name in ['description', 'keywords', 'og:title', 'og:description']:
        pattern = f'<meta[^>]+(?:name|property)=["\'{name}"\'][^>]+content=["\']([^"\']+)["\']'
        match = re.search(pattern, html, re.IGNORECASE)
        if not match:
            pattern = f'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\'{name}"\']'
            match = re.search(pattern, html, re.IGNORECASE)
        if match:
            meta[name] = match.group(1).strip()

    return meta

def scrape_page(url):
    """Scrape a single page and return structured data"""
    print(f"\n  Fetching: {url}")
    html = fetch(url)
    if not html:
        return None

    return {
        'url': url,
        'metadata': extract_metadata(html),
        'nav_links': extract_nav_links(html, BASE_URL),
        'headings': extract_headings(html),
        'paragraphs': extract_paragraphs(html),
        'images': extract_images(html, BASE_URL)[:20],
        'contact': extract_contact_info(html),
        'internal_links': list(extract_links_from_html(html, BASE_URL))[:30],
    }

def main():
    print("=" * 60)
    print("  sunilmerchandising.com Scraper")
    print("=" * 60)

    # Step 1: Scrape homepage
    print("\n[1] Scraping homepage...")
    homepage = scrape_page(BASE_URL)

    if not homepage:
        print("[FATAL] Could not fetch homepage!")
        return

    # Step 2: Discover all pages from nav links
    all_pages_to_scrape = set()
    print(f"\n  Nav links found: {len(homepage['nav_links'])}")
    for link in homepage['nav_links']:
        print(f"    - {link['label']}: {link['href']}")
        all_pages_to_scrape.add(link['href'])

    # Also add internal links
    for link in homepage.get('internal_links', []):
        if 'sunilmerchandising.com' in link:
            all_pages_to_scrape.add(link)

    # Step 3: Scrape each discovered page
    scraped_pages = {'homepage': homepage}

    print(f"\n[2] Scraping {len(all_pages_to_scrape)} discovered pages...")
    for url in sorted(all_pages_to_scrape):
        if url == BASE_URL or url == BASE_URL + '/':
            continue
        # Only scrape sunilmerchandising.com pages
        if 'sunilmerchandising.com' not in url:
            continue
        page_data = scrape_page(url)
        if page_data:
            slug = urlparse(url).path.strip('/').replace('/', '_') or 'index'
            scraped_pages[slug] = page_data

    # Step 4: Save results
    output = {
        'base_url': BASE_URL,
        'total_pages': len(scraped_pages),
        'pages': scraped_pages
    }

    # Pretty summary
    print("\n" + "=" * 60)
    print("  SCRAPING COMPLETE - SUMMARY")
    print("=" * 60)
    print(f"\n  Total pages scraped: {len(scraped_pages)}")

    print("\n  HOMEPAGE METADATA:")
    for k, v in homepage.get('metadata', {}).items():
        print(f"    {k}: {v}")

    print("\n  NAVIGATION STRUCTURE:")
    for link in homepage.get('nav_links', []):
        print(f"    [{link['label']}] -> {link['href']}")

    print("\n  HOMEPAGE HEADINGS:")
    for h in homepage.get('headings', [])[:10]:
        print(f"    <{h['tag']}> {h['text']}")

    print("\n  HOMEPAGE PARAGRAPHS (first 5):")
    for p in homepage.get('paragraphs', [])[:5]:
        print(f"    - {p[:120]}...")

    print("\n  CONTACT INFO:")
    for k, v in homepage.get('contact', {}).items():
        print(f"    {k}: {v}")

    # Save full JSON output
    out_file = '/var/www/html/SagaProject/merchant/site_data.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  [SAVED] Full data saved to: {out_file}")

    # Save readable summary
    summary_file = '/var/www/html/SagaProject/merchant/site_summary.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("SUNIL MERCHANDISING - SITE CONTENT SUMMARY\n")
        f.write("=" * 60 + "\n\n")

        for page_name, page in scraped_pages.items():
            f.write(f"\n{'='*50}\n")
            f.write(f"PAGE: {page_name}\n")
            f.write(f"URL: {page['url']}\n")
            f.write(f"TITLE: {page.get('metadata', {}).get('title', 'N/A')}\n\n")
            f.write("HEADINGS:\n")
            for h in page.get('headings', []):
                f.write(f"  [{h['tag']}] {h['text']}\n")
            f.write("\nCONTENT:\n")
            for p in page.get('paragraphs', [])[:10]:
                f.write(f"  {p}\n\n")
            f.write("\nCONTACT INFO:\n")
            for k, v in page.get('contact', {}).items():
                f.write(f"  {k}: {v}\n")

    print(f"  [SAVED] Summary saved to: {summary_file}")

if __name__ == '__main__':
    main()
