#!/usr/bin/env python3
"""
Parse Google Alerts from MBOX Export
====================================

Extracts news URLs, titles, and sources from Google Alerts emails
exported via Google Takeout.

Usage:
    python scripts/parse_google_alerts.py path/to/alerts.mbox
    python scripts/parse_google_alerts.py path/to/alerts.mbox --output suggestions.yml
    python scripts/parse_google_alerts.py path/to/alerts.mbox --fetch-metadata

Options:
    --output FILE       Save results to YAML file
    --fetch-metadata    Fetch full metadata from URLs (slower but more accurate)
    --limit N           Only process first N emails
    --since DATE        Only process emails since DATE (YYYY-MM-DD)
"""

import argparse
import mailbox
import re
import email
from email.utils import parsedate_to_datetime
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
from html.parser import HTMLParser
from bs4 import BeautifulSoup

import yaml

# Try to import requests for metadata fetching
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class GoogleAlertParser(HTMLParser):
    """Parse Google Alert email HTML to extract article links."""

    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_article = {}
        self.in_title = False
        self.capture_text = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Google Alerts links are typically in <a> tags with Google redirect URLs
        if tag == 'a':
            href = attrs_dict.get('href', '')
            # Google Alerts uses redirect URLs like:
            # https://www.google.com/url?...&url=ACTUAL_URL&...
            if 'google.com/url' in href:
                actual_url = self._extract_actual_url(href)
                if actual_url and self._is_valid_article_url(actual_url):
                    self.current_article = {'url': actual_url}
                    self.in_title = True
                    self.capture_text = True

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_title:
            self.in_title = False
            self.capture_text = False
            if self.current_article.get('url'):
                # Extract source from URL domain
                domain = urlparse(self.current_article['url']).netloc
                self.current_article['source'] = domain.replace('www.', '')
                self.articles.append(self.current_article)
            self.current_article = {}

    def handle_data(self, data):
        if self.capture_text and self.in_title:
            title = data.strip()
            if title and len(title) > 5:  # Skip very short text
                self.current_article['title'] = title

    def _extract_actual_url(self, google_url: str) -> str:
        """Extract the actual URL from a Google redirect URL."""
        try:
            parsed = urlparse(google_url)
            params = parse_qs(parsed.query)
            if 'url' in params:
                return unquote(params['url'][0])
            if 'q' in params:
                return unquote(params['q'][0])
        except Exception:
            pass
        return ''

    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL looks like a valid article URL."""
        if not url.startswith('http'):
            return False
        # Skip Google's own pages
        if 'google.com' in url or 'gstatic.com' in url:
            return False
        # Skip social media
        skip_domains = ['twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com']
        domain = urlparse(url).netloc.lower()
        return not any(skip in domain for skip in skip_domains)


def parse_mbox_email(message) -> dict:
    """Parse a single email message from mbox."""
    result = {
        'subject': message.get('Subject', ''),
        'date': None,
        'articles': []
    }

    # Parse date
    date_str = message.get('Date')
    if date_str:
        try:
            result['date'] = parsedate_to_datetime(date_str)
        except Exception:
            pass

    # Get email body
    body_html = ''
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type == 'text/html':
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        body_html = payload.decode(charset, errors='replace')
                    except Exception:
                        body_html = payload.decode('utf-8', errors='replace')
                break
    else:
        content_type = message.get_content_type()
        if content_type == 'text/html':
            payload = message.get_payload(decode=True)
            if payload:
                charset = message.get_content_charset() or 'utf-8'
                try:
                    body_html = payload.decode(charset, errors='replace')
                except Exception:
                    body_html = payload.decode('utf-8', errors='replace')

    # Parse HTML for articles
    if body_html:
        # Try with custom parser
        parser = GoogleAlertParser()
        try:
            parser.feed(body_html)
            result['articles'] = parser.articles
        except Exception:
            pass

        # If custom parser didn't find anything, try BeautifulSoup
        if not result['articles']:
            result['articles'] = parse_with_beautifulsoup(body_html)

    return result


def parse_with_beautifulsoup(html: str) -> list:
    """Alternative parser using BeautifulSoup."""
    articles = []
    soup = BeautifulSoup(html, 'html.parser')

    for a in soup.find_all('a', href=True):
        href = a['href']

        # Look for Google redirect URLs
        if 'google.com/url' in href:
            # Extract actual URL
            try:
                parsed = urlparse(href)
                params = parse_qs(parsed.query)
                actual_url = None
                if 'url' in params:
                    actual_url = unquote(params['url'][0])
                elif 'q' in params:
                    actual_url = unquote(params['q'][0])

                if actual_url and actual_url.startswith('http'):
                    # Skip Google pages
                    if 'google.com' not in actual_url:
                        title = a.get_text(strip=True)
                        if title and len(title) > 5:
                            domain = urlparse(actual_url).netloc.replace('www.', '')
                            articles.append({
                                'url': actual_url,
                                'title': title,
                                'source': domain
                            })
            except Exception:
                continue

    return articles


def fetch_article_metadata(url: str) -> dict:
    """Fetch additional metadata from the article URL."""
    if not REQUESTS_AVAILABLE:
        return {}

    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        metadata = {}

        # Get better title
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['title'] = og_title.get('content', '')

        # Get site name
        og_site = soup.find('meta', property='og:site_name')
        if og_site:
            metadata['outlet'] = og_site.get('content', '')

        # Get date
        for meta in soup.find_all('meta'):
            prop = meta.get('property', '') or meta.get('name', '')
            if 'date' in prop.lower() or 'published' in prop.lower():
                date_str = meta.get('content', '')
                if date_str:
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                        try:
                            metadata['date'] = datetime.strptime(date_str[:19], fmt)
                            break
                        except ValueError:
                            continue
                    if 'date' in metadata:
                        break

        # Get description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            metadata['description'] = og_desc.get('content', '')[:200]

        return metadata
    except Exception as e:
        print(f"  Warning: Could not fetch metadata for {url}: {e}")
        return {}


def format_source_name(domain: str) -> str:
    """Format domain into a readable source name."""
    # Common mappings
    mappings = {
        'nytimes.com': 'New York Times',
        'washingtonpost.com': 'Washington Post',
        'theguardian.com': 'The Guardian',
        'bbc.com': 'BBC',
        'bbc.co.uk': 'BBC',
        'cnn.com': 'CNN',
        'wired.com': 'WIRED',
        'nature.com': 'Nature',
        'science.org': 'Science',
        'scientificamerican.com': 'Scientific American',
        'physicsworld.com': 'Physics World',
        'quantamagazine.org': 'Quanta Magazine',
        'newyorker.com': 'The New Yorker',
        'vox.com': 'Vox',
        'npr.org': 'NPR',
        'phys.org': 'Phys.org',
        'sciencedaily.com': 'Science Daily',
        'arstechnica.com': 'Ars Technica',
        'symmetrymagazine.org': 'Symmetry Magazine',
        'thedailycardinal.com': 'The Daily Cardinal',
    }

    domain_lower = domain.lower()
    if domain_lower in mappings:
        return mappings[domain_lower]

    # Try to make a readable name from domain
    name = domain.split('.')[0]
    return name.replace('-', ' ').title()


def main():
    parser = argparse.ArgumentParser(description='Parse Google Alerts from MBOX export')
    parser.add_argument('mbox_file', help='Path to the MBOX file')
    parser.add_argument('--output', '-o', help='Output YAML file')
    parser.add_argument('--fetch-metadata', action='store_true',
                        help='Fetch full metadata from URLs')
    parser.add_argument('--limit', type=int, help='Limit number of emails to process')
    parser.add_argument('--since', help='Only process emails since DATE (YYYY-MM-DD)')
    args = parser.parse_args()

    mbox_path = Path(args.mbox_file)
    if not mbox_path.exists():
        print(f"Error: File not found: {mbox_path}")
        return 1

    # Parse since date
    since_date = None
    if args.since:
        try:
            since_date = datetime.strptime(args.since, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format. Use YYYY-MM-DD")
            return 1

    print(f"Parsing MBOX file: {mbox_path}")
    print("=" * 60)

    # Open and parse mbox
    mbox = mailbox.mbox(str(mbox_path))

    all_articles = []
    seen_urls = set()
    email_count = 0

    for i, message in enumerate(mbox):
        if args.limit and i >= args.limit:
            break

        result = parse_mbox_email(message)

        # Filter by date
        if since_date and result['date']:
            if result['date'].replace(tzinfo=None) < since_date:
                continue

        email_count += 1

        for article in result['articles']:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)

                # Add email date as fallback
                if result['date']:
                    article['email_date'] = result['date']

                all_articles.append(article)

    print(f"Processed {email_count} emails")
    print(f"Found {len(all_articles)} unique article URLs")
    print()

    if not all_articles:
        print("No articles found.")
        return 0

    # Optionally fetch metadata
    if args.fetch_metadata:
        print("Fetching article metadata...")
        for i, article in enumerate(all_articles):
            print(f"  [{i+1}/{len(all_articles)}] {article.get('title', '')[:50]}...")
            metadata = fetch_article_metadata(article['url'])
            article.update(metadata)
        print()

    # Format results
    results = []
    for article in all_articles:
        entry = {
            'title': article.get('title', 'Unknown Title'),
            'outlet': article.get('outlet', format_source_name(article.get('source', ''))),
            'category': 'articles',
            'url': article['url'],
        }

        # Use fetched date or email date
        if article.get('date'):
            entry['date'] = article['date'].strftime('%Y-%m-%d')
        elif article.get('email_date'):
            entry['date'] = article['email_date'].strftime('%Y-%m-%d')

        if article.get('description'):
            entry['description'] = article['description']

        results.append(entry)

    # Sort by date (newest first)
    results.sort(key=lambda x: x.get('date', ''), reverse=True)

    # Display results
    print("=" * 60)
    print("ARTICLES FOUND")
    print("=" * 60)
    print()

    for i, entry in enumerate(results[:30], 1):  # Show top 30
        print(f"{i}. {entry['title'][:70]}...")
        print(f"   Source: {entry['outlet']}")
        print(f"   URL: {entry['url'][:70]}...")
        if entry.get('date'):
            print(f"   Date: {entry['date']}")
        print()

    if len(results) > 30:
        print(f"... and {len(results) - 30} more articles")
        print()

    # Output YAML
    print("=" * 60)
    print("YAML FORMAT (copy to media.yml items section):")
    print("=" * 60)
    print()

    yaml_output = yaml.dump(results, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(yaml_output)

    # Save to file
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Extracted from Google Alerts: {mbox_path.name}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total articles: {len(results)}\n\n")
            f.write(yaml_output)
        print(f"Saved to: {output_path}")

    return 0


if __name__ == '__main__':
    exit(main())
