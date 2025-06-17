#!/usr/bin/env python3
"""
CheckLink - Multi-Language Website Link Analyzer

A comprehensive tool for analyzing multi-language websites for broken links, 
scam content, and content relevance issues. Generates professional PDF reports 
organized by language.

Features:
- Multi-language detection and analysis
- Broken link detection (HTTP errors, timeouts)
- AI-powered scam and malicious content detection
- Content relevance scoring
- Professional PDF report generation
- Rate limiting and respectful crawling

Author: Paulino Cristovão
Repository: https://github.com/Paulino-Cristovao/checklink
License: MIT

Usage:
    python checklink.py <URL> [options]
    
Examples:
    python checklink.py https://example.com
    python checklink.py https://site.com --depth 2 --output-dir results
    python checklink.py https://site.com --openai-key "sk-..." --delay 0.5
"""

import requests
import re
import time
import logging
import json
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
import argparse
from dataclasses import dataclass
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import openai
import os
from datetime import datetime
from pathlib import Path


@dataclass
class LinkResult:
    """Data class to store link analysis results"""
    title: str
    url: str
    status: str
    reason: str
    content_snippet: str = ""
    language: str = "unknown"


@dataclass
class LanguageVersion:
    """Data class to store language version information"""
    code: str
    name: str
    url: str


class ContentAnalyzer:
    """AI-powered content analyzer for scam detection and relevance checking"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def analyze_content(self, content: str, main_website_goal: str) -> Dict[str, any]:
        """Analyze content for scam indicators and relevance to main website goal"""
        if not self.api_key:
            return self._fallback_analysis(content, main_website_goal)
        
        try:
            prompt = f"""Analyze this webpage content for relevance and suspicious activity:

Main Website Goal: {main_website_goal}
Content: {content[:2000]}

Respond in JSON format:
{{
    "relevance_score": <1-10>,
    "is_suspicious": <true/false>,
    "reasons": ["reason1", "reason2"],
    "summary": "brief summary"
}}"""
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(content, main_website_goal)
    
    def _fallback_analysis(self, content: str, main_website_goal: str) -> Dict[str, any]:
        """Fallback analysis using keyword matching"""
        content_lower = content.lower()
        
        # Scam indicators
        scam_keywords = [
            'get rich quick', 'guaranteed money', 'click here now',
            'limited time offer', 'act now', 'free money',
            'congratulations you won', 'urgent action required',
            'online casino', 'paypal casino', 'casino bonus', 'casino mit paypal',
            'paypal online casinos', 'fintech news', 'seröse expertenmeinungen',
            'vertrauenswürdigsten paypal online casinos', 'ppc24'
        ]
        
        # Embassy/Mozambique relevance keywords
        embassy_keywords = [
            'embassy', 'consulate', 'mozambique', 'maputo', 'visa', 'passport',
            'diplomatic', 'consular', 'embassy services', 'citizen services',
            'travel document', 'mozambican', 'diplomatic mission'
        ]
        
        suspicious = any(keyword in content_lower for keyword in scam_keywords)
        
        # Enhanced relevance check for embassy/mozambique content
        goal_words = main_website_goal.lower().split()
        embassy_matches = sum(1 for keyword in embassy_keywords if keyword in content_lower)
        goal_matches = sum(1 for word in goal_words if word in content_lower)
        
        # Calculate relevance score (1-10)
        relevance_score = min(10, max(1, (embassy_matches * 3) + (goal_matches * 2)))
        
        # Determine if content is irrelevant
        is_irrelevant = relevance_score < 3 and embassy_matches == 0
        
        reasons = []
        if suspicious:
            reasons.append("Contains suspicious/scam keywords")
        if is_irrelevant:
            reasons.append("Content not related to embassy/diplomatic services")
        
        return {
            "relevance_score": relevance_score,
            "is_suspicious": suspicious,
            "is_irrelevant": is_irrelevant,
            "reasons": reasons,
            "summary": f"Relevance: {relevance_score}/10, Suspicious: {suspicious}, Irrelevant: {is_irrelevant}"
        }


class MultiLanguageLinkChecker:
    """Enhanced link checker with multi-language support"""
    
    def __init__(self, base_url: str, max_depth: int = 2, delay: float = 1.0, output_dir: str = "reports"):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.delay = delay
        self.output_dir = Path(output_dir)
        self.session = self._create_session()
        self.visited_links = set()
        self.main_website_goal = ""
        self.content_analyzer = ContentAnalyzer()
        self.detected_languages: List[LanguageVersion] = []
        
        self.output_dir.mkdir(exist_ok=True)
        self._setup_logging()
    
    def _create_session(self) -> requests.Session:
        """Create configured requests session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_languages(self, soup: BeautifulSoup) -> List[LanguageVersion]:
        """Detect available languages from language switcher"""
        languages = []
        
        # Common language switcher patterns
        selectors = [
            'a[href*="lang="]',
            '.language-switcher a',
            '.lang-switcher a',
            '.qtranxs_language_chooser a',
            '.language-selector a'
        ]
        
        for selector in selectors:
            lang_links = soup.select(selector)
            if lang_links:
                for link in lang_links:
                    href = link.get('href', '')
                    if 'lang=' in href:
                        try:
                            params = parse_qs(urlparse(href).query)
                            if 'lang' in params:
                                lang_code = params['lang'][0]
                                lang_name = link.get_text(strip=True) or lang_code
                                full_url = urljoin(self.base_url, href)
                                
                                if not any(l.code == lang_code for l in languages):
                                    languages.append(LanguageVersion(lang_code, lang_name, full_url))
                        except Exception as e:
                            self.logger.warning(f"Error parsing language link {href}: {e}")
                break
        
        # Fallback to default if no languages detected
        if not languages:
            languages.append(LanguageVersion('default', 'Default', self.base_url))
        
        return languages
    
    def extract_main_goal(self, soup: BeautifulSoup) -> str:
        """Extract main website goal from homepage"""
        # Get meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')[:500]
        
        # Fallback to title and first paragraph
        goal_text = ""
        title = soup.find('title')
        if title:
            goal_text += title.get_text(strip=True) + " "
        
        first_p = soup.find('p')
        if first_p:
            goal_text += first_p.get_text(strip=True)
        
        return goal_text.strip()[:500]
    
    def get_all_links(self, url: str, depth: int = 0) -> List[Tuple[str, str]]:
        """Extract all links from a webpage"""
        if depth > self.max_depth or url in self.visited_links:
            return []
        
        self.visited_links.add(url)
        links = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main goal and detect languages from homepage
            if depth == 0:
                self.main_website_goal = self.extract_main_goal(soup)
                self.detected_languages = self.detect_languages(soup)
                self.logger.info(f"Main website goal: {self.main_website_goal[:100]}...")
                self.logger.info(f"Detected languages: {[lang.code for lang in self.detected_languages]}")
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                title = link.get_text(strip=True) or link.get('title', '') or href
                full_url = urljoin(url, href)
                
                if full_url.startswith(('http://', 'https://')):
                    links.append((title, full_url))
                    
                    # Recursively get links from same domain
                    if depth < self.max_depth and urlparse(full_url).netloc == self.base_domain:
                        links.extend(self.get_all_links(full_url, depth + 1))
            
            time.sleep(self.delay)
            
        except Exception as e:
            self.logger.error(f"Error extracting links from {url}: {e}")
        
        return links
    
    def check_link(self, title: str, url: str, language: str = "unknown") -> Optional[LinkResult]:
        """Check individual link for issues"""
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code >= 400:
                return LinkResult(
                    title=title, url=url, status="BROKEN",
                    reason=f"HTTP {response.status_code}", language=language
                )
            
            # Analyze content
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            
            content = soup.get_text()
            analysis = self.content_analyzer.analyze_content(content, self.main_website_goal)
            
            issues = []
            if analysis['is_suspicious']:
                issues.append(f"SUSPICIOUS: {', '.join(analysis['reasons'])}")
            if analysis['relevance_score'] < 4:
                issues.append(f"LOW RELEVANCE: Score {analysis['relevance_score']}/10")
            
            if issues:
                return LinkResult(
                    title=title, url=url, status="FLAGGED",
                    reason="; ".join(issues), content_snippet=analysis['summary'],
                    language=language
                )
            
            return None
            
        except requests.exceptions.Timeout:
            return LinkResult(title=title, url=url, status="TIMEOUT", reason="Request timeout", language=language)
        except requests.exceptions.ConnectionError:
            return LinkResult(title=title, url=url, status="CONNECTION_ERROR", reason="Connection failed", language=language)
        except Exception as e:
            return LinkResult(title=title, url=url, status="ERROR", reason=str(e), language=language)
    
    def analyze_language_version(self, language: LanguageVersion) -> List[LinkResult]:
        """Analyze a specific language version of the website"""
        self.logger.info(f"Starting analysis of {language.name} ({language.code})")
        self.visited_links.clear()
        
        all_links = self.get_all_links(language.url)
        self.logger.info(f"Found {len(all_links)} links for {language.name}")
        
        problematic_links = []
        for i, (title, url) in enumerate(all_links, 1):
            self.logger.info(f"Checking {i}/{len(all_links)}: {url}")
            
            result = self.check_link(title, url, language.code)
            if result:
                problematic_links.append(result)
                self.logger.warning(f"Issue found: {result.status} - {result.reason}")
            
            time.sleep(self.delay)
        
        return problematic_links
    
    def analyze_all_languages(self) -> Dict[str, List[LinkResult]]:
        """Analyze all detected language versions"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            self.detected_languages = self.detect_languages(soup)
            self.main_website_goal = self.extract_main_goal(soup)
        except Exception as e:
            self.logger.error(f"Error detecting languages: {e}")
            self.detected_languages = [LanguageVersion('default', 'Default', self.base_url)]
        
        results_by_language = {}
        for language in self.detected_languages:
            self.logger.info(f"\n=== Analyzing {language.name} ({language.code}) ===\n")
            results_by_language[language.code] = self.analyze_language_version(language)
        
        return results_by_language


class PDFReportGenerator:
    """Generate PDF reports from link analysis results"""
    
    def __init__(self, results_by_language: Dict[str, List[LinkResult]], website_url: str, output_dir: Path):
        self.results_by_language = results_by_language
        self.website_url = website_url
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_reports(self) -> List[str]:
        """Generate PDF reports"""
        generated_files = []
        
        # Individual language reports
        for language_code, results in self.results_by_language.items():
            filename = self.output_dir / f"link_analysis_{language_code}_{self.timestamp}.pdf"
            self._generate_single_report(results, language_code, str(filename))
            generated_files.append(str(filename))
        
        # Combined report
        combined_filename = self.output_dir / f"link_analysis_combined_{self.timestamp}.pdf"
        self._generate_combined_report(str(combined_filename))
        generated_files.append(str(combined_filename))
        
        return generated_files
    
    def _create_table(self, results: List[LinkResult]) -> Table:
        """Create formatted table from results"""
        table_data = [['Title', 'URL', 'Issue']]
        
        for result in results:
            title = (result.title[:50] + "...") if len(result.title) > 50 else result.title
            url = (result.url[:60] + "...") if len(result.url) > 60 else result.url
            reason = (result.reason[:80] + "...") if len(result.reason) > 80 else result.reason
            table_data.append([title, url, reason])
        
        table = Table(table_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        return table
    
    def _generate_single_report(self, results: List[LinkResult], language_code: str, filename: str):
        """Generate PDF report for a single language"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                   fontSize=16, textColor=colors.darkblue, alignment=1)
        
        story.extend([
            Paragraph(f"Link Analysis Report - {language_code.upper()}", title_style),
            Paragraph(f"Website: {self.website_url}", styles['Normal']),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
            Spacer(1, 20),
            Paragraph(f"Summary: {len(results)} issues found", styles['Heading2']),
            Spacer(1, 12)
        ])
        
        if results:
            story.append(self._create_table(results))
        else:
            story.append(Paragraph("No issues found! All links are working properly.", styles['Normal']))
        
        doc.build(story)
    
    def _generate_combined_report(self, filename: str):
        """Generate combined report with all languages"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                   fontSize=16, textColor=colors.darkblue, alignment=1)
        
        total_issues = sum(len(results) for results in self.results_by_language.values())
        
        story.extend([
            Paragraph("Multi-Language Link Analysis Report", title_style),
            Paragraph(f"Website: {self.website_url}", styles['Normal']),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
            Spacer(1, 20),
            Paragraph(f"Total Issues: {total_issues}", styles['Heading2']),
            Spacer(1, 12)
        ])
        
        # Summary by language
        for language_code, results in self.results_by_language.items():
            story.append(Paragraph(f"{language_code.upper()}: {len(results)} issues", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Detailed results
        for language_code, results in self.results_by_language.items():
            if results:
                story.extend([
                    Paragraph(f"Issues in {language_code.upper()}", styles['Heading2']),
                    Spacer(1, 12),
                    self._create_table(results),
                    Spacer(1, 20)
                ])
        
        if total_issues == 0:
            story.append(Paragraph("No issues found across all languages!", styles['Normal']))
        
        doc.build(story)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Multi-language website link checker')
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('--depth', type=int, default=5, help='Maximum crawl depth (default: 5)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (default: 1.0)')
    parser.add_argument('--output-dir', '-o', default='reports', help='Output directory (default: reports)')
    parser.add_argument('--openai-key', help='OpenAI API key for content analysis')
    
    args = parser.parse_args()
    
    if args.openai_key:
        os.environ['OPENAI_API_KEY'] = args.openai_key
    
    # Run analysis
    checker = MultiLanguageLinkChecker(args.url, args.depth, args.delay, args.output_dir)
    results_by_language = checker.analyze_all_languages()
    
    # Generate reports
    report_generator = PDFReportGenerator(results_by_language, args.url, checker.output_dir)
    report_files = report_generator.generate_reports()
    
    # Print summary
    total_issues = sum(len(results) for results in results_by_language.values())
    print(f"\n=== Analysis Complete ===")
    print(f"Analyzed {len(results_by_language)} language versions")
    print(f"Found {total_issues} total issues")
    print(f"\nReports generated:")
    for report_file in report_files:
        print(f"- {report_file}")
    
    print(f"\nIssues by language:")
    for language_code, results in results_by_language.items():
        print(f"- {language_code.upper()}: {len(results)} issues")
        for result in results[:3]:  # Show first 3
            print(f"  • {result.title[:50]}: {result.status}")
        if len(results) > 3:
            print(f"  • ... and {len(results) - 3} more")


if __name__ == "__main__":
    main()