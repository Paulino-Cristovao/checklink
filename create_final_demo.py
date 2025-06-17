#!/usr/bin/env python3
"""
Create comprehensive final demo reports with all issue types
"""

from checklink import PDFReportGenerator, LinkResult
from pathlib import Path
from datetime import datetime

def create_comprehensive_demo():
    """Create comprehensive demo showing all CheckLink capabilities"""
    
    # Create comprehensive demo with realistic scenarios
    results_by_language = {
        'PT': [
            # Real issue from actual analysis
            LinkResult(
                title="Centro de Promoção de Investimentos", 
                url="http://www.cpi.co.mz",
                status="FLAGGED",
                reason="SUSPICIOUS: Contains suspicious/scam keywords",
                language="PT"
            ),
            # Simulated broken links for demonstration
            LinkResult(
                title="Página de Contactos Antiga", 
                url="https://ambassademozambiquefrance.fr/contact-antigo?lang=PT",
                status="BROKEN",
                reason="HTTP 404 - Page Not Found",
                language="PT"
            ),
            LinkResult(
                title="Documento PDF Removido", 
                url="https://ambassademozambiquefrance.fr/docs/regulamento-2019.pdf",
                status="BROKEN",
                reason="HTTP 410 - Gone (Resource permanently removed)",
                language="PT"
            ),
            LinkResult(
                title="Servidor Consular Indisponível", 
                url="https://services.consulado-mozambique.fr/down",
                status="BROKEN",
                reason="HTTP 503 - Service Unavailable",
                language="PT"
            ),
            LinkResult(
                title="Link Externo com Timeout", 
                url="http://www.mozambique-gov-slow.mz",
                status="TIMEOUT",
                reason="Request timeout after 10 seconds",
                language="PT"
            )
        ],
        'fr': [
            # Real issue from actual analysis
            LinkResult(
                title="Centre de Promotion d'Investissement", 
                url="http://www.cpi.co.mz",
                status="FLAGGED",
                reason="SUSPICIOUS: Contains suspicious/scam keywords",
                language="fr"
            ),
            # Simulated broken links for demonstration
            LinkResult(
                title="Ancienne Page Contact", 
                url="https://ambassademozambiquefrance.fr/contact-ancien?lang=fr",
                status="BROKEN",
                reason="HTTP 404 - Page Not Found",
                language="fr"
            ),
            LinkResult(
                title="Accès Refusé Administration", 
                url="https://ambassademozambiquefrance.fr/admin/private",
                status="BROKEN",
                reason="HTTP 403 - Forbidden (Access denied)",
                language="fr"
            ),
            LinkResult(
                title="Site Externe Inaccessible", 
                url="http://broken-mozambique-ministry.gov.mz",
                status="CONNECTION_ERROR",
                reason="Connection failed - DNS resolution error",
                language="fr"
            ),
            LinkResult(
                title="Site de Jeux Suspects", 
                url="http://casino-mozambique-fake.com",
                status="FLAGGED",
                reason="SUSPICIOUS: Contains promotional language; Content not related to embassy/diplomatic services",
                language="fr"
            )
        ],
        'en': [
            # Real issue from actual analysis
            LinkResult(
                title="Investment Promotion Centre", 
                url="http://www.cpi.co.mz",
                status="FLAGGED",
                reason="SUSPICIOUS: Contains suspicious/scam keywords",
                language="en"
            ),
            # Simulated broken links for demonstration
            LinkResult(
                title="Old Contact Page", 
                url="https://ambassademozambiquefrance.fr/contact-old?lang=en",
                status="BROKEN",
                reason="HTTP 404 - Page Not Found",
                language="en"
            ),
            LinkResult(
                title="Broken Redirect Chain", 
                url="https://ambassademozambiquefrance.fr/redirect-broken-chain",
                status="BROKEN",
                reason="HTTP 301 -> HTTP 404 - Redirect to non-existent page",
                language="en"
            ),
            LinkResult(
                title="Internal Server Error", 
                url="https://ambassademozambiquefrance.fr/system/error-page",
                status="BROKEN",
                reason="HTTP 500 - Internal Server Error",
                language="en"
            ),
            LinkResult(
                title="Suspicious External Site", 
                url="http://phishing-embassy-fake.example",
                status="FLAGGED",
                reason="SUSPICIOUS: Contains suspicious/scam keywords; Content not related to embassy/diplomatic services",
                language="en"
            )
        ]
    }
    
    # Generate reports in final_reports directory
    output_dir = Path("final_reports")
    website_url = "https://ambassademozambiquefrance.fr/?lang=PT"
    
    # Create timestamp for demo reports
    demo_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + "_DEMO"
    
    # Generate demo reports with special naming
    for language_code, results in results_by_language.items():
        filename = output_dir / f"comprehensive_demo_{language_code}_{demo_timestamp}.pdf"
        generator = PDFReportGenerator({language_code: results}, website_url, output_dir)
        generator.timestamp = demo_timestamp.replace("_DEMO", "")
        generator._generate_single_report(results, language_code, str(filename))
        print(f"Generated: {filename}")
    
    # Generate combined demo report
    combined_filename = output_dir / f"comprehensive_demo_combined_{demo_timestamp}.pdf"
    generator = PDFReportGenerator(results_by_language, website_url, output_dir)
    generator.timestamp = demo_timestamp.replace("_DEMO", "")
    generator._generate_combined_report(str(combined_filename))
    print(f"Generated: {combined_filename}")
    
    total_issues = sum(len(results) for results in results_by_language.values())
    print(f"\n=== Comprehensive Demo Complete ===")
    print(f"Total issues demonstrated: {total_issues}")
    print(f"Languages: PT, FR, EN")
    print(f"Issue types showcased:")
    print(f"  - BROKEN: HTTP 404, 403, 410, 500, 503")
    print(f"  - TIMEOUT: Network timeouts")
    print(f"  - CONNECTION_ERROR: DNS failures")  
    print(f"  - FLAGGED: Suspicious/scam content")
    
    return len(results_by_language)

if __name__ == "__main__":
    create_comprehensive_demo()