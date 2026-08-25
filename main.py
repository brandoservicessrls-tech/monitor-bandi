import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Keywords for Italian safety engineering
KEYWORDS = [
    'rspp', 'cse', 'csp', 'sicurezza', '81/08', 
    'coordinatore', 'antincendio', 'formazione', 
    'medico competente', 'dpi', 'valutazione rischio'
]

def scrape_ted_tenders():
    """Scrape TED for Italian tenders"""
    try:
        # TED website for Italian tenders
        url = "https://ted.europa.eu/TED/browse/browseByCountry.html?countryCode=IT"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tenders = []
        
        # Extract tender information (simplified parsing)
        for item in soup.find_all('tr')[:20]:  # Limit to first 20
            cols = item.find_all('td')
            if len(cols) >= 3:
                title = cols[0].text.strip()
                deadline = cols[2].text.strip() if len(cols) > 2 else "N/A"
                
                # Check if tender matches safety keywords
                if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                    tenders.append({
                        'title': title,
                        'deadline': deadline,
                        'source': 'TED'
                    })
        
        return tenders
    except Exception as e:
        print(f"Error scraping TED: {e}")
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

def format_tender_message(tenders):
    """Format tenders into Telegram message"""
    if not tenders:
        return "Nessun bando trovato nelle ultime 24 ore."
    
    message = f"<b>🔍 Bandi Trovati - {datetime.now().strftime('%d/%m/%Y %H:%M')}</b>\n\n"
    
    for i, tender in enumerate(tenders, 1):
        message += f"<b>{i}. {tender['title'][:50]}...</b>\n"
        message += f"   📅 Scadenza: {tender['deadline']}\n"
        message += f"   📌 Fonte: {tender['source']}\n\n"
    
    message += f"<i>Bot di monitoraggio bandi - {datetime.now().strftime('%H:%M:%S')}</i>"
    return message

def main():
    """Main function"""
    print("BetaIngegneriaBot - Starting tender monitoring...")
    
    # Scrape tenders
    tenders = scrape_ted_tenders()
    
    if tenders:
        # Format and send message
        message = format_tender_message(tenders)
        if send_telegram_message(message):
            print(f"✅ Message sent successfully with {len(tenders)} tenders")
        else:
            print("❌ Failed to send Telegram message")
    else:
        print("No relevant tenders found")

if __name__ == "__main__":
    main()
