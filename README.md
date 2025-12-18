# LinkCheck 🔗

> **Dead Link Checker** - Scan websites for broken links and generate comprehensive reports. Perfect for SEO audits and website maintenance.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Active](https://img.shields.io/badge/status-active-success.svg)](https://github.com/yksanjo/LinkCheck)
[![GitHub stars](https://img.shields.io/github/stars/yksanjo/LinkCheck?style=social)](https://github.com/yksanjo/LinkCheck)

**LinkCheck** crawls your website to find broken links, generating detailed reports with status codes, response times, and link locations. Essential for SEO audits, website maintenance, and ensuring a great user experience.

## Features

- 🔍 Recursive link scanning
- 📊 Broken link reports
- 🔗 Internal and external link checking
- ⚡ Fast parallel checking
- 📈 Link health metrics
- 📤 Export to CSV/JSON
- 🌐 Respect robots.txt

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Check Website

```bash
python checker.py https://example.com
```

### Check with Depth Limit

```bash
python checker.py https://example.com --max-depth 2
```

### Export Report

```bash
python checker.py https://example.com --export report.csv
```

### Check Specific Pages

```bash
python checker.py https://example.com --pages /page1 /page2
```

## Output

The checker generates:
- List of broken links
- HTTP status codes
- Link locations (which page contains the broken link)
- Response times
- Link types (internal/external)

## License

MIT License


