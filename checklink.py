#!/usr/bin/env python3
"""
CheckLink - Comprehensive Website Link Checker and Content Analyzer
Analyzes websites for broken links, scam content, and relevance issues.
"""

import requests
import re
import time
import logging
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional, Set
import argparse
from dataclasses import dataclass
from reportlab.lib.pagesizes import letter, A4
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
        """
        Analyze content for scam indicators and relevance to main website goal
        Returns dict with relevance score and scam indicators
        """
        if not self.api_key:
            return self._fallback_analysis(content, main_website_goal)
        
        try:
            prompt = f"""
            You are an intelligent content evaluator. Analyze the following webpage content:

            Main Website Goal: {main_website_goal}
            
            Content: {content[:2000]}  # Limit content to avoid token limits
            
            Evaluate based on:
            1. Relevance to main website goal (scale 1-10)
            2. Scam/suspicious indicators (yes/no with reasons)
            
            Respond in JSON format:
            {{
                "relevance_score": <1-10>,
                "is_suspicious": <true/false>,
                "reasons": ["reason1", "reason2"],
                "summary": "brief summary"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return eval(result)  # Simple JSON parsing - in production use json.loads
            
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
            'suspicious activity', 'verify account immediately'
        ]
        
        suspicious = any(keyword in content_lower for keyword in scam_keywords)
        
        # Basic relevance check
        goal_words = main_website_goal.lower().split()
        relevance_score = sum(1 for word in goal_words if word in content_lower)
        relevance_score = min(10, max(1, relevance_score * 2))
        
        return {
            "relevance_score": relevance_score,
            "is_suspicious": suspicious,
            "reasons": ["Keyword-based analysis"] if suspicious else [],
            "summary": f"Relevance: {relevance_score}/10, Suspicious: {suspicious}"
        }


class MultiLanguageLinkChecker:
    """Enhanced link checker with multi-language support"""
    
    def __init__(self, base_url: str, max_depth: int = 2, delay: float = 1.0, output_dir: str = "reports"):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.delay = delay
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.visited_links = set()
        self.results = []
        self.main_website_goal = ""
        self.content_analyzer = ContentAnalyzer()
        self.detected_languages: List[LanguageVersion] = []
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_languages(self, soup: BeautifulSoup) -> List[LanguageVersion]:
        """Detect available languages from language switcher"""
        languages = []
        
        # Common language switcher patterns
        language_selectors = [
            'a[href*="lang="]',
            '.language-switcher a',
            '.lang-switcher a',
            '.qtranxs_language_chooser a',
            '.language-selector a',
            '[class*="language"] a[href*="lang"]'
        ]
        
        for selector in language_selectors:
            lang_links = soup.select(selector)
            if lang_links:
                for link in lang_links:
                    href = link.get('href', '')
                    if 'lang=' in href:
                        # Extract language code from URL parameter
                        try:
                            parsed_url = urlparse(href)
                            if parsed_url.query:
                                params = parse_qs(parsed_url.query)
                                if 'lang' in params:
                                    lang_code = params['lang'][0]
                                    lang_name = link.get_text(strip=True) or link.get('title', '') or lang_code
                                    full_url = urljoin(self.base_url, href)
                                    
                                    # Avoid duplicates
                                    if not any(l.code == lang_code for l in languages):
                                        languages.append(LanguageVersion(
                                            code=lang_code,
                                            name=lang_name,
                                            url=full_url
                                        ))
                        except Exception as e:
                            self.logger.warning(f"Error parsing language link {href}: {e}")
                break  # Use first matching selector
        
        # If no languages detected, check current URL for lang parameter
        if not languages:
            parsed_current = urlparse(self.base_url)
            if parsed_current.query and 'lang=' in parsed_current.query:
                params = parse_qs(parsed_current.query)
                if 'lang' in params:
                    current_lang = params['lang'][0]
                    languages.append(LanguageVersion(
                        code=current_lang,
                        name=current_lang.upper(),
                        url=self.base_url
                    ))
        
        # Add default language if none detected
        if not languages:
            languages.append(LanguageVersion(
                code='default',
                name='Default',
                url=self.base_url
            ))
        
        return languages
    
    def extract_main_goal(self, soup: BeautifulSoup, language: str = "unknown") -> str:
        """Extract main website goal from homepage"""
        # Try to find mission/about information
        goal_elements = soup.find_all(['h1', 'h2', 'meta', 'p'], 
                                    attrs={'name': ['description', 'keywords'],
                                           'class': re.compile(r'(about|mission|purpose)', re.I)})
        
        goal_text = ""
        for element in goal_elements:
            if element.name == 'meta':
                goal_text += element.get('content', '') + " "
            else:
                goal_text += element.get_text(strip=True) + " "
        
        # Fallback to title and first paragraph
        if not goal_text.strip():
            title = soup.find('title')
            first_p = soup.find('p')
            if title:
                goal_text += title.get_text(strip=True) + " "
            if first_p:
                goal_text += first_p.get_text(strip=True)
        
        return goal_text.strip()[:500]  # Limit length
    
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
                
                # Convert relative URLs to absolute
                full_url = urljoin(url, href)
                
                # Skip non-HTTP links
                if not full_url.startswith(('http://', 'https://')):
                    continue
                
                links.append((title, full_url))
                
                # Recursively get links from same domain
                if depth < self.max_depth and urlparse(full_url).netloc == self.base_domain:
                    links.extend(self.get_all_links(full_url, depth + 1))
            
            time.sleep(self.delay)  # Rate limiting
            
        except Exception as e:
            self.logger.error(f"Error extracting links from {url}: {e}")
        
        return links
    
    def check_link(self, title: str, url: str, language: str = "unknown") -> LinkResult:
        """Check individual link for issues"""
        try:
            response = self.session.get(url, timeout=10)
            
            # Check HTTP status
            if response.status_code >= 400:
                return LinkResult(
                    title=title,
                    url=url,
                    status="BROKEN",
                    reason=f"HTTP {response.status_code} - {response.reason}",
                    language=language
                )
            
            # Get content for analysis
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            content = soup.get_text()
            content_snippet = content[:1000]  # First 1000 chars for analysis
            
            # Analyze content
            analysis = self.content_analyzer.analyze_content(content, self.main_website_goal)
            
            # Check for issues
            issues = []
            
            if analysis['is_suspicious']:
                issues.append(f"SUSPICIOUS: {', '.join(analysis['reasons'])}")
            
            if analysis['relevance_score'] < 4:
                issues.append(f"LOW RELEVANCE: Score {analysis['relevance_score']}/10")
            
            if issues:
                return LinkResult(
                    title=title,
                    url=url,
                    status="FLAGGED",
                    reason="; ".join(issues),
                    content_snippet=analysis['summary'],
                    language=language
                )
            
            return None  # No issues found
            
        except requests.exceptions.Timeout:
            return LinkResult(title=title, url=url, status="TIMEOUT", reason="Request timeout", language=language)
        except requests.exceptions.ConnectionError:
            return LinkResult(title=title, url=url, status="CONNECTION_ERROR", reason="Connection failed", language=language)
        except Exception as e:
            return LinkResult(title=title, url=url, status="ERROR", reason=str(e), language=language)
    
    def analyze_language_version(self, language: LanguageVersion) -> List[LinkResult]:
        """Analyze a specific language version of the website"""
        self.logger.info(f"Starting analysis of {language.name} ({language.code}) version: {language.url}")
        
        # Reset visited links for each language
        self.visited_links.clear()
        
        # Get all links for this language version
        all_links = self.get_all_links(language.url)
        self.logger.info(f"Found {len(all_links)} links to check for {language.name}")
        
        # Check each link
        problematic_links = []
        for i, (title, url) in enumerate(all_links, 1):
            self.logger.info(f"Checking link {i}/{len(all_links)} for {language.name}: {url}")
            
            result = self.check_link(title, url, language.code)
            if result:
                problematic_links.append(result)
                self.logger.warning(f"Issue found in {language.name}: {result.status} - {result.reason}")
            
            time.sleep(self.delay)  # Rate limiting
        
        return problematic_links
    
    def analyze_all_languages(self) -> Dict[str, List[LinkResult]]:
        """Analyze all detected language versions"""
        # First, detect languages from the base URL
        try:
            response = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            self.detected_languages = self.detect_languages(soup)
            self.main_website_goal = self.extract_main_goal(soup)
        except Exception as e:
            self.logger.error(f"Error detecting languages: {e}")
            # Fallback to single language
            self.detected_languages = [LanguageVersion('default', 'Default', self.base_url)]
        
        results_by_language = {}
        
        for language in self.detected_languages:
            self.logger.info(f"\n=== Analyzing {language.name} ({language.code}) ===\n")
            results = self.analyze_language_version(language)
            results_by_language[language.code] = results
        
        return results_by_language


class MultiLanguagePDFReportGenerator:
    """Generate PDF reports from multi-language link analysis results"""
    
    def __init__(self, results_by_language: Dict[str, List[LinkResult]], website_url: str, output_dir: Path):
        self.results_by_language = results_by_language
        self.website_url = website_url
        self.output_dir = output_dir
    
    def generate_reports(self) -> List[str]:
        """Generate separate PDF reports for each language"""
        generated_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for language_code, results in self.results_by_language.items():
            filename = self.output_dir / f"link_analysis_{language_code}_{timestamp}.pdf"
            report_file = self.generate_single_report(results, language_code, str(filename))
            generated_files.append(report_file)
        
        # Generate combined report
        combined_filename = self.output_dir / f"link_analysis_combined_{timestamp}.pdf"
        combined_file = self.generate_combined_report(str(combined_filename))
        generated_files.append(combined_file)
        
        return generated_files
    
    def generate_single_report(self, results: List[LinkResult], language_code: str, filename: str) -> str:
        """Generate PDF report for a single language"""
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        
        # Title
        story.append(Paragraph(f"Website Link Analysis Report - {language_code.upper()}", title_style))
        story.append(Paragraph(f"Website: {self.website_url}", styles['Normal']))
        story.append(Paragraph(f"Language: {language_code.upper()}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph(f"Summary: Found {len(results)} problematic links in {language_code.upper()}", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if not results:
            story.append(Paragraph(f"No issues found in {language_code.upper()}! All links are working properly and content is relevant.", styles['Normal']))
        else:
            # Create table data
            table_data = [['Page/Link Title', 'URL', 'Issue Description']]
            
            for result in results:
                # Wrap long text
                title = result.title[:50] + "..." if len(result.title) > 50 else result.title
                url = result.url[:60] + "..." if len(result.url) > 60 else result.url
                reason = result.reason[:80] + "..." if len(result.reason) > 80 else result.reason
                
                table_data.append([title, url, reason])
            
            # Create table
            table = Table(table_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(table)
        
        # Build PDF
        doc.build(story)
        return filename
    
    def generate_combined_report(self, filename: str) -> str:
        """Generate combined report with all languages"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            alignment=1
        )
        
        # Title
        story.append(Paragraph("Multi-Language Website Link Analysis Report", title_style))
        story.append(Paragraph(f"Website: {self.website_url}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Overall summary
        total_issues = sum(len(results) for results in self.results_by_language.values())
        story.append(Paragraph(f"Overall Summary: Found {total_issues} total issues across all languages", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Summary by language
        for language_code, results in self.results_by_language.items():
            story.append(Paragraph(f"{language_code.upper()}: {len(results)} issues", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Detailed results by language
        for language_code, results in self.results_by_language.items():
            if results:
                story.append(Paragraph(f"Issues in {language_code.upper()}", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Create table data
                table_data = [['Page/Link Title', 'URL', 'Issue Description']]
                
                for result in results:
                    title = result.title[:50] + "..." if len(result.title) > 50 else result.title
                    url = result.url[:60] + "..." if len(result.url) > 60 else result.url
                    reason = result.reason[:80] + "..." if len(result.reason) > 80 else result.reason
                    
                    table_data.append([title, url, reason])
                
                # Create table
                table = Table(table_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
        
        if total_issues == 0:
            story.append(Paragraph("No issues found across all languages! All links are working properly.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return filename


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Check multi-language website links for issues')
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('--depth', type=int, default=2, help='Maximum crawl depth (default: 2)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--output-dir', '-o', default='reports', help='Output directory for reports (default: reports)')
    parser.add_argument('--openai-key', help='OpenAI API key for advanced content analysis')
    
    args = parser.parse_args()
    
    # Set OpenAI key if provided
    if args.openai_key:
        os.environ['OPENAI_API_KEY'] = args.openai_key
    
    # Initialize checker
    checker = MultiLanguageLinkChecker(args.url, max_depth=args.depth, delay=args.delay, output_dir=args.output_dir)
    
    # Analyze all language versions
    results_by_language = checker.analyze_all_languages()
    
    # Generate reports
    report_generator = MultiLanguagePDFReportGenerator(results_by_language, args.url, checker.output_dir)
    report_files = report_generator.generate_reports()
    
    # Print summary
    total_issues = sum(len(results) for results in results_by_language.values())
    print(f"\n=== Analysis Complete ===")
    print(f"Analyzed {len(results_by_language)} language versions")
    print(f"Found {total_issues} total problematic links")
    print(f"\nReports generated:")
    for report_file in report_files:
        print(f"- {report_file}")
    
    # Print summary by language
    print(f"\nIssues by language:")
    for language_code, results in results_by_language.items():
        print(f"- {language_code.upper()}: {len(results)} issues")
        if results:
            for result in results[:3]:  # Show first 3 per language
                print(f"  • {result.title[:50]}: {result.status} - {result.reason[:50]}")
            if len(results) > 3:
                print(f"  • ... and {len(results) - 3} more (see PDF reports)")


if __name__ == "__main__":
    main()