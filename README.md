# Dead Link Checker

Scan websites for broken links and generate comprehensive reports. Perfect for SEO audits and website maintenance.

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


