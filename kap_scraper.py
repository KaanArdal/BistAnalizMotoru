import requests
from bs4 import BeautifulSoup
import re
import json

class KAPScraper:
    def __init__(self):
        self.base_url = "https://halkarz.com/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_latest_ipo_text(self):
        """
        halkarz.com üzerinden en son eklenen halka arzın detay sayfasına girer
        ve tüm metni yapay zeka analizi için ham olarak çeker.
        """
        print("Güncel Halka Arz Taranıyor (halkarz.com)...")
        try:
            r = requests.get(self.base_url, headers=self.headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Ana sayfadaki ilk halka arz linkini bul
            latest_ipo_link = None
            for h3 in soup.find_all('h3'):
                a_tag = h3.find('a')
                if a_tag and a_tag.has_attr('href'):
                    latest_ipo_link = a_tag['href']
                    break
                    
            if not latest_ipo_link:
                return None
                
            print(f"Detay sayfasına gidiliyor: {latest_ipo_link}")
            r_detail = requests.get(latest_ipo_link, headers=self.headers, timeout=10)
            r_detail.raise_for_status()
            soup_detail = BeautifulSoup(r_detail.text, 'html.parser')
            
            # Sayfadaki tüm gereksiz script ve stilleri temizle
            for script in soup_detail(["script", "style"]):
                script.extract()
                
            text_content = soup_detail.get_text(separator=' ', strip=True)
            return text_content
            
        except Exception as e:
            print(f"Halka arz detayı çekilirken hata: {e}")
            return None

    def get_all_recent_ipos(self):
        """halkarz.com'daki son halka arzların listesini getirir."""
        try:
            r = requests.get(self.base_url, headers=self.headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            liste = []
            for h3 in soup.find_all('h3', class_='halka-arz-baslik') or soup.find_all('h3'):
                a_tag = h3.find('a')
                if a_tag and a_tag.has_attr('href'):
                    baslik = a_tag.text.strip()
                    # Kod h3'ün parent div'inde yer alıyor (Örn: 'INTETİntetra Teknoloji...')
                    parent_text = h3.parent.get_text(strip=True)
                    kod_match = re.match(r'^([A-Z]{4,5})', parent_text)
                    kod = kod_match.group(1) if kod_match else "BİLİNMİYOR"
                    liste.append({"isim": baslik, "kod": kod, "url": a_tag['href']})
            return liste[:10]
        except Exception:
            return []

    def search_ipo_text(self, kod):
        """Verilen koda sahip halka arzın detay metnini bulur ve çeker."""
        liste = self.get_all_recent_ipos()
        hedef_url = None
        for item in liste:
            if item["kod"] == kod:
                hedef_url = item["url"]
                break
                
        if not hedef_url:
            return None
            
        try:
            r = requests.get(hedef_url, headers=self.headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            return soup.get_text(separator=' ', strip=True)
        except Exception:
            return None

    def get_active_ipos(self):
        """Turnover radarı için son halka arzları ve lot sayılarını otomatik çeker."""
        son_halkaarzlar = self.get_all_recent_ipos()[:2] # Sadece en son 2 halka arzı takip et
        aktif_liste = []
        
        for item in son_halkaarzlar:
            kod = item["kod"]
            url = item["url"]
            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                text_content = soup.get_text(separator=' ', strip=True)
                
                # Lot sayısını regex ile bulmaya çalış (Örn: 120.000.000 Lot, 15.500.000 Pay)
                lot_match = re.search(r'([\d\.]+)\s*(?:Lot|Pay)', text_content, re.IGNORECASE)
                if lot_match:
                    lot_str = lot_match.group(1).replace('.', '')
                    lot_sayisi = int(lot_str)
                    aktif_liste.append({"kodu": kod, "lot": lot_sayisi})
                else:
                    # Bulunamazsa varsayılan veya yfinance shares
                    aktif_liste.append({"kodu": kod, "lot": 50_000_000})
            except Exception as e:
                print(f"{kod} için lot aranırken hata: {e}")
                
        return aktif_liste

if __name__ == "__main__":
    scraper = KAPScraper()
    results = scraper.get_recent_halka_arz_results()
    for res in results:
        ratios = scraper.parse_demand_ratio(res["text"])
        print(f"Şirket: {res['company']}")
        print(f"Oranlar: {ratios}")
