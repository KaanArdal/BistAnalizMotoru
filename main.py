import time
import sys
import schedule

# Konsolda Türkçe karakter hatasını (UnicodeEncodeError) çözmek için:
sys.stdout.reconfigure(encoding='utf-8')
from kap_scraper import KAPScraper
from izahname_analyzer import IzahnameAnalyzer
from tahta_filtresi import TahtaFiltresi
from turnover_radar import TurnoverRadar
from telegram_bot import send_telegram_message

def job_halka_arz_analizi():
    """
    KAP/Halkarz.com üzerinden yeni halka arz sonuçlarını kontrol eder ve raporlar.
    """
    print("Halka arz analizi başlatılıyor...")
    scraper = KAPScraper()
    analyzer = IzahnameAnalyzer()

    # Halkarz.com'dan en son halka arzın tüm metnini çek
    raw_text = scraper.get_latest_ipo_text()
    
    if not raw_text:
        print("Halka arz metni bulunamadı.")
        return
        
    print("Yapay Zeka (Gemini) metni analiz ediyor...")
    # Metni tamamen Gemini'ye ver, o parse etsin ve direkt telegram raporu formatında versin
    rapor = analyzer.analyze_halka_arz(raw_text)

    # Telegrama gönder
    send_telegram_message(rapor)

def job_turnover_kontrol():
    """
    Modül 4: Aktif işlem gören halka arzları izler. (Örnek: Her 30 dakikada bir)
    """
    print("El değiştirme radarı çalışıyor...")
    radar = TurnoverRadar()
    
    # Takip edilecek aktif yeni halka arzları otomatik çek (halkarz.com'dan yakalanan son kodlar)
    scraper = KAPScraper()
    takip_listesi = scraper.get_active_ipos()
    
    if not takip_listesi:
        print("Şu an takip edilecek güncel halka arz kodu bulunamadı.")
        return
    
    for hisse in takip_listesi:
        sonuc = radar.check_turnover(hisse["kodu"], hisse["lot"])
        if sonuc and sonuc["uyari"]:
            mesaj = f"🚨 <b>{sonuc['hisse_kodu']} EL DEĞİŞTİRME UYARISI!</b> 🚨\n"
            mesaj += f"Günlük Hacim: {sonuc['gunluk_hacim']:,} Lot\n"
            mesaj += f"Toplam Halka Açık Lot: {sonuc['toplam_halka_acik_lot']:,} Lot\n"
            mesaj += f"⚠️ <b>El Değiştirme Oranı: %{sonuc['el_degistirme_orani']}</b>\n\n"
            mesaj += "Balinalar mal boşaltıyor olabilir, tavan bozulma riski mevcut!"
            
            send_telegram_message(mesaj)

if __name__ == "__main__":
    print("Bot başlatılıyor. İlk test çalışmaları yapılıyor...")
    send_telegram_message("🤖 <b>Bot Aktif:</b> Görevler zamanlandı. BIST Halka Arz Motoru devrede!")
    
    # Başlangıçta test için birer kez çalıştır
    job_halka_arz_analizi()
    job_turnover_kontrol()
    
    # Zamanlayıcılar (Scheduler)
    # Halka arz sonuçları günde 1 kez kontrol edilebilir
    schedule.every().day.at("18:30").do(job_halka_arz_analizi)
    
    # Radar borsa açıkken (10:00 - 18:00 arası) daha sık kontrol etmeli (örn her saat başı)
    # Basitlik için her saat başı diyelim
    schedule.every(1).hours.do(job_turnover_kontrol)
    
    print("Zamanlayıcı çalışıyor. Çıkmak için CTRL+C yapın.")
    while True:
        schedule.run_pending()
        time.sleep(60)
