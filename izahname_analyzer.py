import os
from google import genai
import config
import pdfplumber
import sys

sys.stdout.reconfigure(encoding='utf-8')

class IzahnameAnalyzer:
    def __init__(self):
        # Yeni genai SDK client'ını oluşturuyoruz.
        if config.GEMINI_API_KEY:
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        else:
            self.client = None
            
        self.model_name = 'gemini-3.6-flash'

    def extract_text_from_pdf(self, pdf_path):
        """
        Verilen PDF dosyasından metin çıkarır.
        Özellikle 'Fon Kullanım Yeri' kelimelerinin geçtiği sayfaları hedefler.
        """
        extracted_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
        except Exception as e:
            print(f"PDF okuma hatası: {e}")
        return extracted_text

    def analyze_halka_arz(self, text):
        """
        Gemini API'sini kullanarak halkarz.com ham metninden tüm detayları çıkarır.
        """
        if not self.client:
            return "Hata: Gemini API Key bulunamadı."

        prompt = f"""
        Aşağıdaki metin halkarz.com sitesindeki bir şirketin detay sayfasından tamamen kopyalanmıştır. Bu metne bakarak şu bilgileri bul ve çıkar:

        1. Şirket Adı ve Borsa Kodu (Örn: LILAK)
        2. Kurumsal ve Bireysel Talep Katı (Örn: Kurumsal 5.2x, Bireysel 2.1x) Eğer henüz açıklanmamışsa 'Açıklanmadı' yaz.
        3. Toplam Halka Arz Büyüklüğü (TL cinsinden) ve Tahta Tipi (Eğer 500 Milyon TL altıysa Sığ Tahta, 2 Milyar TL üstüyse Derin Tahta, arasıysa Orta Tahta yaz).
        4. Fon Kullanım Yeri Özeti (Şirket elde edeceği geliri ne yapacak? Borca mı yatırıma mı?)
        5. Yatırımcı Tavsiyesi: 
           - "🟢 KESİN KATIL": Fonların büyük kısmı yeni yatırımlara, Ar-Ge'ye, kapasite artışına gidiyorsa.
           - "🟡 RİSKE DEĞEBİLİR": Fonların bir kısmı borç ödemeye gitse de, kayda değer bir kısmı büyüme ve yatırıma ayrılmışsa.
           - "🔴 UZAK DUR (KIRMIZI BAYRAK)": Gelir neredeyse tamamen mevcut borçları kapatmaya veya işletme sermayesi açığını yamamaya gidiyorsa.

        Cevabını doğrudan Telegram mesajı atılacak şekilde şık, emojili ve net bir formatta ver. Fazladan giriş veya gelişme cümlesi kurma.
        
        Metin:
        {text[:15000]}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print(f"Gemini API hatası: {e}")
            return f"Analiz yapılamadı: {e}"

if __name__ == "__main__":
    # Test
    pass
