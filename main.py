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

# Italian Regional Portals for Tenders
REGIONAL_PORTALS = {
    'Abruzzo': 'https://www.abruzzolavori.regione.abruzzo.it/',
    'Basilicata': 'https://www.basilicatalavori.basilicata.it/',
    'Calabria': 'https://www.calabrialavori.calabria.it/',
    'Campania': 'https://www.lavoripubblici.campania.it/',
    'Emilia-Romagna': 'https://www.parer.it/',
    'Friuli-Venezia Giulia': 'https://www.friuli.xpubblica.it/',
    'Lazio': 'https://www.lavoripubblici.lazio.it/',
    'Liguria': 'https://www.ligurialavori.regione.liguria.it/',
    'Lombardia': 'https://www.bandi.regione.lombardia.it/',
    'Marche': 'https://www.marcheprocura.marche.it/',
    'Molise': 'https://www.moliselavori.molise.it/',
    'Piemonte': 'https://www.piemontelavori.piemonte.it/',
    'Puglia': 'https://www.puglia.it/web/appalti-pubblici',
    'Sardegna': 'https://www.sardegnalavori.sardegna.it/',
    'Sicilia': 'https://appalti.regionesiciliana.lavoripubblici.sicilia.it/gare/',
    'Toscana': 'https://www.toscanalavori.it/',
    'Trentino-Alto Adige': 'https://www.trentinolavori.tn.it/',
    'Umbria': 'https://www.umbrialavori.umbria.it/',
    'Valle d\'Aosta': 'https://www.aostalavori.vda.it/',
    'Veneto': 'https://www.venetolavori.it/'
}

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

def scrape_all_regional_portals():
    """Scrape all 20 Italian regional tender portals"""
    all_regional_tenders = []

    for region, url in REGIONAL_PORTALS.items():
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract links and text
            for item in soup.find_all('a', limit=8):
                text = item.text.strip()
                if text and any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                    all_regional_tenders.append({
                        'title': text[:80],
                        'deadline': 'Consultare Regione',
                        'source': f'Bandi {region}'
                    })
        except Exception as e:
            print(f"Error scraping {region}: {e}")

    return all_regional_tenders

def scrape_roga_italia():
    """Scrape ROGA Italia for safety engineering tenders"""
    try:
        url = "https://www.rogaitalia.com/Account/ListaEmail"
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
                    'deadline': 'Consultare ROGA Italia',
                    'source': 'ROGA Italia'
                })

        return tenders
    except Exception as e:
        print(f"Error scraping ROGA Italia: {e}")
        return []

def scrape_bandi_gare_dappalto():
    """Scrape BandiGareDappalto.it - National portal for all Italian public tenders"""
    try:
        url = "https://www.bandigaredappalto.it/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []

        for item in soup.find_all('a', limit=15):
            text = item.text.strip()
            if text and any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                tenders.append({
                    'title': text[:80],
                    'deadline': 'Consultare BandiGareDappalto',
                    'source': 'BandiGareDappalto (Italia)'
                })

        return tenders
    except Exception as e:
        print(f"Error scraping BandiGareDappalto: {e}")
        return []

def scrape_banchedati():
    """Scrape Banchedati.biz - Platform with 40K+ monthly tenders from all Italian municipalities"""
    try:
        url = "https://www.banchedati.biz/bandi-di-gara/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []

        for item in soup.find_all('a', limit=15):
            text = item.text.strip()
            if text and any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                tenders.append({
                    'title': text[:80],
                    'deadline': 'Consultare Banchedati',
                    'source': 'Banchedati (40K+ bandi/mese)'
                })

        return tenders
    except Exception as e:
        print(f"Error scraping Banchedati: {e}")
        return []

def scrape_telemat():
    """Scrape Telemat - Italian tenders and public procurement platform"""
    try:
        url = "https://areaclienti.telemat.it/index.html"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []

        for item in soup.find_all('a', limit=15):
            text = item.text.strip()
            if text and any(keyword.lower() in text.lower() for keyword in KEYWORDS):
                tenders.append({
                    'title': text[:80],
                    'deadline': 'Consultare Telemat',
                    'source': 'Telemat (Appalti Pubblici)'
                })

        return tenders
    except Exception as e:
        print(f"Error scraping Telemat: {e}")
        return []

def scrape_mepa_consip():
    """Scrape MEPA and Consip e-procurement platforms"""
    try:
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
        return "🔔 Nessun bando nuovo trovato oggi per l'Italia."

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
        if len(items) > 3:
            message += f"  ... e {len(items) - 3} altri\n"
        message += "\n"

    message += f"<i>🤖 Bot monitoraggio bandi - Sicurezza sul Lavoro (D.Lgs. 81/08)</i>\n"
    message += f"<i>Total: {len(all_tenders)} bandi trovati</i>"
    return message

def main():
    """Main function - Scrape all sources"""
    print("BetaIngegneriaBot - Starting comprehensive tender monitoring (20 regions + 9 national sources)...")

    # Scrape all sources
    all_tenders = []

    print("Scraping TED...")
    all_tenders.extend(scrape_ted_tenders())

    print("Scraping Gazzetta Ufficiale...")
    all_tenders.extend(scrape_gazzetta_ufficiale())

    print("Scraping ANAC...")
    all_tenders.extend(scrape_anac_tenders())

    print("Scraping all 20 Italian Regional Portals...")
    all_tenders.extend(scrape_all_regional_portals())

    print("Scraping ROGA Italia...")
    all_tenders.extend(scrape_roga_italia())

    print("Scraping BandiGareDappalto.it (National)...")
    all_tenders.extend(scrape_bandi_gare_dappalto())

    print("Scraping Banchedati.biz (40K+ tenders/month)...")
    all_tenders.extend(scrape_banchedati())

    print("Scraping Telemat (Appalti Pubblici)...")
    all_tenders.extend(scrape_telemat())

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
            print(f"✅ Message sent successfully with {len(unique_tenders)} tenders from all sources")
        else:
            print("❌ Failed to send Telegram message")
    else:
        print("No relevant tenders found across all sources")

if __name__ == "__main__":
    main()
