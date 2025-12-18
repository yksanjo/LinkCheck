#!/usr/bin/env python3
"""
Dead Link Checker
Scan websites for broken links and generate reports
"""

import os
import sys
import argparse
import json
import time
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class DeadLinkChecker:
    def __init__(self, base_url: str, max_depth: int = 3, max_workers: int = 10):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_workers = max_workers
        
        self.visited_urls: Set[str] = set()
        self.broken_links: List[Dict] = []
        self.valid_links: List[Dict] = []
        self.link_map: Dict[str, List[str]] = {}  # url -> [pages that link to it]
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and should be checked"""
        parsed = urlparse(url)
        
        # Skip non-HTTP(S) URLs
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Skip mailto, tel, javascript, etc.
        if parsed.scheme in ['mailto', 'tel', 'javascript', 'data']:
            return False
        
        # Skip anchors only
        if url.startswith('#'):
            return False
        
        return True
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL"""
        # Remove fragment
        if '#' in url:
            url = url.split('#')[0]
        
        # Remove trailing slash (except for root)
        if url.endswith('/') and urlparse(url).path != '/':
            url = url.rstrip('/')
        
        return url
    
    def check_link(self, url: str, source_page: str = None) -> Dict:
        """Check if a single link is broken"""
        try:
            start_time = time.time()
            response = self.session.head(url, allow_redirects=True, timeout=10)
            response_time = time.time() - start_time
            
            # Some servers don't support HEAD, try GET
            if response.status_code == 405:
                start_time = time.time()
                response = self.session.get(url, timeout=10, stream=True)
                response_time = time.time() - start_time
            
            status_code = response.status_code
            
            result = {
                'url': url,
                'status_code': status_code,
                'response_time': round(response_time, 2),
                'source_page': source_page,
                'is_broken': status_code >= 400,
                'checked_at': datetime.now().isoformat()
            }
            
            return result
        except requests.exceptions.Timeout:
            return {
                'url': url,
                'status_code': 0,
                'response_time': None,
                'source_page': source_page,
                'is_broken': True,
                'error': 'Timeout',
                'checked_at': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            return {
                'url': url,
                'status_code': 0,
                'response_time': None,
                'source_page': source_page,
                'is_broken': True,
                'error': 'Connection Error',
                'checked_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'url': url,
                'status_code': 0,
                'response_time': None,
                'source_page': source_page,
                'is_broken': True,
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    def extract_links(self, url: str) -> List[str]:
        """Extract all links from a page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            # Find all <a> tags
            for tag in soup.find_all('a', href=True):
                href = tag['href']
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                absolute_url = self.normalize_url(absolute_url)
                
                if self.is_valid_url(absolute_url):
                    links.append(absolute_url)
            
            return links
        except Exception as e:
            print(f"❌ Error extracting links from {url}: {e}")
            return []
    
    def is_same_domain(self, url: str) -> bool:
        """Check if URL is on the same domain"""
        return urlparse(url).netloc == self.domain
    
    def scan_page(self, url: str, depth: int = 0, source_page: str = None):
        """Recursively scan a page for links"""
        if depth > self.max_depth:
            return
        
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        print(f"🔍 Scanning: {url} (depth: {depth})")
        
        # Extract links
        links = self.extract_links(url)
        
        # Track which pages link to which URLs
        for link in links:
            if link not in self.link_map:
                self.link_map[link] = []
            if url not in self.link_map[link]:
                self.link_map[link].append(url)
        
        # Check links (only external or if we're not recursing)
        links_to_check = []
        internal_links = []
        
        for link in links:
            if not self.is_same_domain(link):
                # External link - always check
                links_to_check.append((link, url))
            else:
                # Internal link
                internal_links.append(link)
                # Check it if we haven't seen it
                if link not in self.visited_urls:
                    links_to_check.append((link, url))
        
        # Check links in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.check_link, link_url, source_page or url): link_url
                for link_url, _ in links_to_check
            }
            
            for future in as_completed(futures):
                result = future.result()
                
                if result['is_broken']:
                    self.broken_links.append(result)
                    print(f"❌ Broken: {result['url']} (Status: {result.get('status_code', 'Error')})")
                else:
                    self.valid_links.append(result)
        
        # Recursively scan internal links
        if depth < self.max_depth:
            for link in internal_links:
                if link not in self.visited_urls:
                    self.scan_page(link, depth + 1, url)
    
    def scan(self, start_urls: List[str] = None):
        """Start scanning"""
        if start_urls:
            urls_to_scan = [self.normalize_url(urljoin(self.base_url, url)) for url in start_urls]
        else:
            urls_to_scan = [self.base_url]
        
        print(f"🚀 Starting link check for {self.base_url}")
        print(f"   Max depth: {self.max_depth}")
        print(f"   Workers: {self.max_workers}")
        print()
        
        for url in urls_to_scan:
            self.scan_page(url)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive report"""
        total_links = len(self.broken_links) + len(self.valid_links)
        broken_count = len(self.broken_links)
        valid_count = len(self.valid_links)
        
        # Group broken links by status code
        broken_by_status = {}
        for link in self.broken_links:
            status = link.get('status_code', 'Error')
            broken_by_status[status] = broken_by_status.get(status, 0) + 1
        
        return {
            'scan_date': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_pages_scanned': len(self.visited_urls),
            'total_links_checked': total_links,
            'broken_links_count': broken_count,
            'valid_links_count': valid_count,
            'broken_percentage': round((broken_count / total_links * 100) if total_links > 0 else 0, 2),
            'broken_by_status': broken_by_status,
            'broken_links': self.broken_links,
            'valid_links': self.valid_links
        }
    
    def export_csv(self, filename: str):
        """Export broken links to CSV"""
        import pandas as pd
        
        if not self.broken_links:
            print("No broken links to export")
            return
        
        df = pd.DataFrame(self.broken_links)
        df.to_csv(filename, index=False)
        print(f"✅ Exported {len(self.broken_links)} broken links to {filename}")
    
    def export_json(self, filename: str):
        """Export full report to JSON"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ Exported report to {filename}")
    
    def print_summary(self):
        """Print summary report"""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("LINK CHECK SUMMARY")
        print("="*80)
        print(f"Base URL: {report['base_url']}")
        print(f"Pages Scanned: {report['total_pages_scanned']}")
        print(f"Total Links Checked: {report['total_links_checked']}")
        print(f"Valid Links: {report['valid_links_count']}")
        print(f"Broken Links: {report['broken_links_count']} ({report['broken_percentage']}%)")
        
        if report['broken_by_status']:
            print("\nBroken Links by Status Code:")
            for status, count in sorted(report['broken_by_status'].items()):
                print(f"  {status}: {count}")
        
        if self.broken_links:
            print("\nTop Broken Links:")
            for link in self.broken_links[:10]:
                status = link.get('status_code', 'Error')
                source = link.get('source_page', 'Unknown')
                print(f"  ❌ {link['url']}")
                print(f"     Status: {status} | Source: {source}")


def main():
    parser = argparse.ArgumentParser(description='Dead Link Checker')
    parser.add_argument('url', help='Base URL to check')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum crawl depth')
    parser.add_argument('--max-workers', type=int, default=10, help='Number of parallel workers')
    parser.add_argument('--pages', nargs='+', help='Specific pages to check')
    parser.add_argument('--export', help='Export report to CSV file')
    parser.add_argument('--json', help='Export full report to JSON file')
    
    args = parser.parse_args()
    
    checker = DeadLinkChecker(args.url, args.max_depth, args.max_workers)
    
    try:
        checker.scan(args.pages)
        checker.print_summary()
        
        if args.export:
            checker.export_csv(args.export)
        
        if args.json:
            checker.export_json(args.json)
    except KeyboardInterrupt:
        print("\n⚠️  Scan interrupted by user")
        checker.print_summary()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


