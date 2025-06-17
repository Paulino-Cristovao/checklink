# CheckLink - Multi-Language Website Link Analyzer

<div align="center">

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

*A comprehensive tool for analyzing multi-language websites for broken links, scam content, and content relevance issues*

</div>

## 🎯 Project Objectives

CheckLink is designed to solve critical website maintenance challenges by providing:

1. **Automated Link Validation** - Detect broken links, timeouts, and HTTP errors across entire websites
2. **Multi-Language Support** - Automatically discover and analyze all language versions of a website  
3. **Scam Detection** - Use AI and keyword analysis to identify suspicious or malicious content
4. **Content Relevance Analysis** - Evaluate if content aligns with the website's main purpose
5. **Professional Reporting** - Generate organized PDF reports for stakeholders
6. **Scalable Analysis** - Handle websites of any size with configurable depth and rate limiting

### Target Use Cases

- **Website Administrators** - Regular health checks and maintenance
- **SEO Professionals** - Link integrity audits and content quality assessment
- **Security Teams** - Detection of malicious or compromised content
- **Compliance Officers** - Ensuring content relevance and brand consistency
- **Digital Agencies** - Client website auditing and reporting

## ✨ Key Features

### 🌐 Multi-Language Intelligence
- **Automatic Language Detection** - Discovers all available language versions
- **Language-Specific Analysis** - Separate reports for each language (PT, FR, EN, etc.)
- **URL Parameter Handling** - Supports `?lang=` parameter patterns
- **Comprehensive Coverage** - Analyzes all language variants systematically

### 🔍 Advanced Link Analysis
- **HTTP Status Checking** - Detects 4xx/5xx errors, redirects, and timeouts
- **Connection Monitoring** - Identifies network and DNS issues
- **Content Validation** - Analyzes page content for issues
- **External Link Tracking** - Monitors third-party link integrity

### 🛡️ Content Security & Quality
- **AI-Powered Scam Detection** - Uses OpenAI GPT-4 for sophisticated analysis
- **Keyword-Based Fallback** - Casino, phishing, and spam detection
- **Relevance Scoring** - Evaluates content alignment with website goals
- **Suspicious Pattern Recognition** - Identifies common scam indicators

### 📊 Professional Reporting
- **Individual Language Reports** - Separate PDF for each language
- **Combined Analysis Report** - Overview across all languages  
- **Three-Column Format** - Title, URL, Issue Description
- **Executive Summary** - High-level statistics and insights

### ⚙️ Enterprise-Ready Features
- **Rate Limiting** - Respectful crawling with configurable delays
- **Depth Control** - Limit analysis scope to manage resources
- **Session Management** - Persistent connections for efficiency
- **Error Recovery** - Robust handling of network issues
- **Logging & Monitoring** - Detailed progress tracking

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Paulino-Cristovao/checklink.git
cd checklink

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Analyze a website with default settings
python checklink.py https://example.com

# Quick scan with limited depth
python checklink.py https://example.com --depth 1 --output-dir results
```

### Advanced Usage

```bash
# Full analysis with AI-powered content checking
python checklink.py https://ambassademozambiquefrance.fr/?lang=PT \
    --depth 2 \
    --delay 0.5 \
    --output-dir embassy_analysis \
    --openai-key "your-openai-api-key"
```

## 📖 Detailed Usage Guide

### Command Line Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | *required* | Website URL to analyze |
| `--depth` | integer | `5` | Maximum crawl depth (0-10 recommended) |
| `--delay` | float | `1.0` | Delay between requests in seconds |
| `--output-dir` | string | `reports` | Directory for generated reports |
| `--openai-key` | string | *optional* | OpenAI API key for advanced analysis |

### Configuration Options

#### Crawl Depth Guidelines
- **Depth 0**: Homepage only (fastest, good for quick checks)
- **Depth 1**: Homepage + direct links (balanced)
- **Depth 2**: Two levels deep (comprehensive for most sites)
- **Depth 3+**: Full site analysis (use for critical audits)

#### Rate Limiting
- **0.1-0.5s**: Fast scanning (use with permission)
- **1.0s**: Default (respectful crawling)
- **2.0s+**: Conservative (for sensitive or slow sites)

### Environment Variables

```bash
# Optional: Set OpenAI API key globally
export OPENAI_API_KEY="your-api-key-here"

# Run analysis
python checklink.py https://example.com
```

## 📁 Output Structure

CheckLink generates organized reports in the specified output directory:

```
reports/
├── link_analysis_PT_20250617_143432.pdf      # Portuguese issues
├── link_analysis_fr_20250617_143432.pdf      # French issues  
├── link_analysis_en_20250617_143432.pdf      # English issues
└── link_analysis_combined_20250617_143432.pdf # All languages
```

### Report Contents

Each PDF report includes:

1. **Executive Summary**
   - Total issues found
   - Language-specific statistics
   - Generation timestamp

2. **Issue Table** (3-column format)
   - **Page/Link Title**: Human-readable page identifier
   - **URL**: Full URL of problematic link
   - **Issue Description**: Detailed problem explanation

3. **Issue Categories**
   - `BROKEN`: HTTP 4xx/5xx errors
   - `TIMEOUT`: Request timeouts or slow responses
   - `CONNECTION_ERROR`: Network connectivity issues
   - `FLAGGED`: Suspicious or irrelevant content
   - `ERROR`: Unexpected errors during analysis

## 🔧 Configuration & Customization

### Adding Custom Scam Keywords

Edit the `scam_keywords` list in `checklink.py`:

```python
scam_keywords = [
    'get rich quick', 'guaranteed money', 'click here now',
    'your-custom-keywords-here'
]
```

### Customizing Language Detection

Modify the `selectors` list to match your website's language switcher:

```python
selectors = [
    'a[href*="lang="]',           # Standard parameter
    '.your-language-selector a',   # Custom CSS class
]
```

### AI Content Analysis

For enhanced scam detection, provide an OpenAI API key:

```bash
# Set environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Or pass directly
python checklink.py https://example.com --openai-key "sk-your-key-here"
```

## 🎨 Example Use Cases

### 1. Embassy Website Audit

```bash
python checklink.py https://ambassademozambiquefrance.fr/?lang=PT \
    --depth 1 \
    --output-dir embassy_audit \
    --delay 0.5
```

**Results**: Detected 3 languages, analyzed 162 links, found 3 suspicious external links

### 2. E-commerce Site Health Check

```bash
python checklink.py https://mystore.com \
    --depth 2 \
    --output-dir store_health_check \
    --openai-key "sk-..." \
    --delay 1.0
```

### 3. Quick Blog Validation

```bash
python checklink.py https://myblog.com \
    --depth 0 \
    --output-dir blog_check
```

## 📊 Understanding Results

### Interpreting Issue Types

| Issue Type | Severity | Action Required |
|------------|----------|-----------------|
| `BROKEN` | High | Fix or remove broken links |
| `TIMEOUT` | Medium | Check server performance |
| `CONNECTION_ERROR` | Medium | Verify external dependencies |
| `FLAGGED` | Variable | Review content for relevance/security |

### Performance Metrics

- **Links/Minute**: Depends on delay setting and site responsiveness
- **Memory Usage**: Minimal (designed for efficiency)
- **Network Impact**: Respectful crawling with built-in rate limiting

## 🛠️ Development & Contributing

### Project Structure

```
checklink/
├── checklink.py          # Main application
├── requirements.txt      # Python dependencies
└── README.md            # This documentation
```

### Key Classes

- `MultiLanguageLinkChecker`: Core analysis engine
- `ContentAnalyzer`: AI-powered content evaluation
- `PDFReportGenerator`: Professional report creation
- `LanguageVersion`: Language metadata container

### Development Setup

```bash
# Clone and setup
git clone https://github.com/Paulino-Cristovao/checklink.git
cd checklink

# Install development dependencies
pip install -r requirements.txt

# Run tests
python checklink.py https://example.com --depth 0
```

## 🔒 Security & Privacy

- **No Data Storage**: Analysis results are only saved locally
- **Respectful Crawling**: Built-in rate limiting and user-agent identification
- **API Key Safety**: OpenAI keys are only used for content analysis
- **Network Security**: HTTPS preferred, HTTP fallback available

## 📋 Requirements

### System Requirements
- **Python**: 3.7 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB for dependencies + output space
- **Network**: Internet connection for analysis

### Python Dependencies
- `requests` ≥ 2.28.0 - HTTP client
- `beautifulsoup4` ≥ 4.11.0 - HTML parsing
- `reportlab` ≥ 3.6.0 - PDF generation  
- `openai` ≥ 0.27.0 - AI content analysis
- `lxml` ≥ 4.9.0 - XML/HTML processing

## 🆘 Troubleshooting

### Common Issues

**Issue**: "No languages detected"
- **Solution**: Check if website uses `?lang=` parameters or update language selectors

**Issue**: "Too many timeouts"
- **Solution**: Increase `--delay` parameter or check network connectivity

**Issue**: "OpenAI API errors"
- **Solution**: Verify API key validity and account credits

**Issue**: "PDF generation fails"
- **Solution**: Ensure write permissions in output directory

### Performance Optimization

1. **Reduce depth** for faster analysis
2. **Increase delay** for more stable connections
3. **Use depth 0** for quick health checks
4. **Specify output directory** to organize results

## 📄 License

This project is licensed under the MIT License - see the repository for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/Paulino-Cristovao/checklink/issues)
- **Documentation**: This README
- **Examples**: See usage examples above

---

<div align="center">

**Built with ❤️ for website quality assurance**

*CheckLink - Ensuring your website's integrity across all languages*

</div>