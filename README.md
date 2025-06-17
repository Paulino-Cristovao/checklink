# CheckLink - Multi-Language Website Link Analyzer

A comprehensive tool that analyzes multi-language websites for broken links, scam content, and content relevance issues. Generates detailed PDF reports with findings organized by language.

## Features

- **Multi-Language Support**: Automatically detects and analyzes all language versions
- **Link Validation**: Checks all links on a website for HTTP errors
- **Content Analysis**: Uses AI to detect scam/suspicious content
- **Relevance Checking**: Analyzes if content aligns with website's main goal
- **Organized PDF Reports**: Generates separate reports per language + combined report
- **Recursive Crawling**: Analyzes links across multiple pages
- **Rate Limiting**: Respectful crawling with configurable delays

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up OpenAI API for advanced content analysis:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Usage
```bash
python checklink.py https://example.com
```

### Advanced Options
```bash
python checklink.py https://ambassademozambiquefrance.fr/?lang=PT \
    --depth 1 \
    --delay 0.5 \
    --output-dir embassy_reports \
    --openai-key "your-key"
```

### Parameters
- `url`: Website URL to analyze (required)
- `--depth`: Maximum crawl depth (default: 2)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--output-dir`: Output directory for reports (default: reports)
- `--openai-key`: OpenAI API key for advanced analysis

## Output

The tool generates multiple PDF reports organized by language:
- **Individual Language Reports**: Separate PDF for each detected language (PT, FR, EN, etc.)
- **Combined Report**: Single PDF with all languages and issues
- **Organized Structure**: Reports saved in specified output directory

Each report contains a table with three columns:
1. **Page/Link Title**: Title of the problematic page/link
2. **URL**: The specific URL that has issues  
3. **Issue Description**: Detailed reason for the problem

### Issue Types
- **BROKEN**: HTTP 4xx/5xx errors
- **TIMEOUT**: Request timeouts
- **CONNECTION_ERROR**: Network connection failures
- **SUSPICIOUS**: Potential scam/malicious content detected
- **LOW RELEVANCE**: Content not relevant to main website goal

## Examples

### Analyze embassy website (multi-language):  
```bash
python checklink.py https://ambassademozambiquefrance.fr/?lang=PT \
    --depth 1 \
    --output-dir embassy_reports
```

### Deep analysis with AI:
```bash
python checklink.py https://mystore.com \
    --depth 3 \
    --delay 2.0 \
    --openai-key "sk-..." \
    --output-dir store_analysis
```

## How It Works

1. **Goal Extraction**: Analyzes homepage to understand website's main purpose
2. **Link Discovery**: Recursively finds all links up to specified depth
3. **Link Testing**: Tests each link for HTTP errors and timeouts
4. **Content Analysis**: Downloads and analyzes page content for:
   - Scam indicators (suspicious keywords, misleading claims)
   - Relevance to main website goal
5. **Report Generation**: Creates PDF with all problematic links

## Notes

- Without OpenAI API key, uses keyword-based fallback analysis
- Respects robots.txt and includes rate limiting
- Only crawls links within the same domain by default
- Generates timestamped reports automatically

## Requirements

- Python 3.7+
- Internet connection
- Optional: OpenAI API key for advanced analysis