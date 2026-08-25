import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Keywords for Italian safety engineering
KEYWORDS = [
    'rspp', 'cse', 'csp', 'sicurezza', '81/08', 
    'coordinatore', 'antincendio', 'formazione', 
    'medico competente', 'dpi', 'valutazione rischio',
    'responsabile sicurezza', 'spp', 'prevenzione'
]

def scrape_ted_tenders():
    """Scrape TED (Tenders Electronic Daily) for Italian tenders"""
    try:
        url = "https://ted.europa.eu/TED/browse/browseByCountry.html?countryCode=IT"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []
        
        for item in soup.find_all('tr')[:15]:
            cols = item.find_all('td')
            if len(cols) >= 3:
                title = cols[0].text.strip()
                deadline = cols[2].text.strip() if len(cols) > 2 else "N/A"
                
                if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                    tenders.append({
                        'title': title[:80],
                        'deadline': deadline,
                        'source': 'TED (Europa)'
                    })
        
        return tenders
    except Exception as e:
        print(f"Error scraping TED: {e}")
        return []

def scrape_gazzetta_ufficiale():
    """Scrape Gazzetta Ufficiale for Italian tenders"""
    try:
        # Gazzetta Ufficiale appalti pubblici
        url = "https://www.gazzettaufficiale.it/eli/id/2024/01/01/trama"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []
        
        for item in soup.find_all('a', limit=10):
            text = item.text.strip()
            if any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                tenders.append({
                    'title': text[:80],
                    'deadline': 'Consultare Gazzetta',
                    'source': 'Gazzetta Ufficiale'
                })
        
        return tenders
    except Exception as e:
        print(f"Error scraping Gazzetta Ufficiale: {e}")
        return []

def scrape_anac_tenders():
    """Scrape ANAC (Autorità Nazionale Anticorruzione) tenders"""
    try:
        # ANAC - Appalti Pubblici
        url = "https://www.anticorruzione.it/portal/public/classic/Contenuto/Bandi"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []
        
        for item in soup.find_all('div', class_='news-item', limit=10):
            text = item.get_text()
            if any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                title = item.find('h3')
                if title:
                    tenders.append({
                        'title': title.text.strip()[:80],
                        'deadline': 'Consultare ANAC',
                        'source': 'ANAC'
                    })
        
        return tenders
    except Exception as e:
        print(f"Error scraping ANAC: {e}")
        return []

def scrape_regional_portals():
    """Scrape Italian regional portals for tenders"""
    regional_tenders = []
    
    # Lombardy
    try:
        url = "https://www.bandi.regione.lombardia.it/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for item in soup.find_all('a', limit=5):
            text = item.text.strip()
            if any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                regional_tenders.append({
                    'title': text[:80],
                    'deadline': 'Consultare Regione',
                    'source': 'Bandi Lombardia'
                })
    except Exception as e:
        print(f"Error scraping Lombardia: {e}")
    
    # Lazio
    try:
        url = "https://www.lazio.it/cittadino/bandi"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for item in soup.find_all('a', limit=5):
            text = item.text.strip()
            if any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                regional_tenders.append({
                    'title': text[:80],
                    'deadline': 'Consultare Regione',
                    'source': 'Bandi Lazio'
                })
    except Exception as e:
        print(f"Error scraping Lazio: {e}")
    
    return regional_tenders

def scrape_mepa_consip():
    """Scrape MEPA and Consip e-procurement platforms"""
    try:
        # MEPA - Marketplace Elettronico della Pubblica Amministrazione
        url = "https://www.acquistinretepa.it/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []
        
        for item in soup.find_all('tr', limit=10):
            text = item.get_text()
            if any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                cols = item.find_all('td')
                if len(cols) > 0:
                    tenders.append({
                        'title': cols[0].text.strip()[:80],
                        'deadline': 'Consultare MEPA',
                        'source': 'MEPA/Consip'
                    })
        
        return tenders
    except Exception as e:
        print(f"Error scraping MEPA/Consip: {e}")
        return []

def send_telegram_message(message):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def format_tender_message(all_tenders):
    """Format tenders into Telegram message"""
    if not all_tenders:
        return "Nessun bando trovato nelle ultime 24 ore."
    
    message = f"<b>🔍 Bandi di Sicurezza Trovati - {datetime.now().strftime('%d/%m/%Y %H:%M')}</b>\n\n"
    
    # Group by source
    sources = {}
    for tender in all_tenders:
        source = tender['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(tender)
    
    # Format by source
    for source, items in sources.items():
        message += f"<b>📌 {source}</b>\n"
        for i, tender in enumerate(items[:3], 1):
            message += f"  {i}. {tender['title']}\n"
            message += f"     📅 {tender['deadline']}\n"
        message += "\n"
    
    message += f"<i>Bot monitoraggio bandi - Sicurezza sul Lavoro</i>\n"
    message += f"<i>{datetime.now().strftime('%H:%M:%S')}</i>"
    return message

def main():
    """Main function - Scrape all sources"""
    print("BetaIngegneriaBot - Starting comprehensive tender monitoring...")
    
    # Scrape all sources
    all_tenders = []
    
    print("Scraping TED...")
    all_tenders.extend(scrape_ted_tenders())
    
    print("Scraping Gazzetta Ufficiale...")
    all_tenders.extend(scrape_gazzetta_ufficiale())
    
    print("Scraping ANAC...")
    all_tenders.extend(scrape_anac_tenders())
    
    print("Scraping Regional Portals...")
    all_tenders.extend(scrape_regional_portals())
    
    print("Scraping MEPA/Consip...")
    all_tenders.extend(scrape_mepa_consip())
    
    # Remove duplicates
    unique_tenders = []
    seen = set()
    for tender in all_tenders:
        key = (tender['title'], tender['source'])
        if key not in seen:
            seen.add(key)
            unique_tenders.append(tender)
    
    if unique_tenders:
        message = format_tender_message(unique_tenders)
        if send_telegram_message(message):
            print(f"✅ Message sent successfully with {len(unique_tenders)} tenders from multiple sources")
        else:
            print("❌ Failed to send Telegram message")
    else:
        print("No relevant tenders found across all sources")

if __name__ == "__main__":
    main()
