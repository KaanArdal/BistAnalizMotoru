import yfinance as yf

class TurnoverRadar:
    def __init__(self):
        # El değiştirme uyarı eşiği (Örn: %15)
        self.uyari_esigi = 15.0

    def check_turnover(self, hisse_kodu, toplam_halka_acik_lot):
        """
        Verilen hisse kodunun günlük hacmini çeker ve el değiştirme oranını hesaplar.
        Uyarı eşiğini geçerse sinyal üretir.
        """
        # Yahoo Finance BIST hisselerini "IS" takısıyla tutar (Örn: THYAO.IS)
        yf_ticker = f"{hisse_kodu}.IS"
        
        try:
            ticker = yf.Ticker(yf_ticker)
            # Günlük veriyi çek
            data = ticker.history(period="1d")
            
            if data.empty:
                print(f"{hisse_kodu} için veri bulunamadı. Halka arz henüz işleme başlamamış olabilir.")
                return None
                
            gunluk_hacim = data['Volume'].iloc[-1]
            
            el_degistirme_orani = (gunluk_hacim / toplam_halka_acik_lot) * 100
            
            uyari_ver = el_degistirme_orani > self.uyari_esigi
            
            return {
                "hisse_kodu": hisse_kodu,
                "gunluk_hacim": int(gunluk_hacim),
                "toplam_halka_acik_lot": toplam_halka_acik_lot,
                "el_degistirme_orani": round(el_degistirme_orani, 2),
                "uyari": uyari_ver
            }
            
        except Exception as e:
            print(f"{hisse_kodu} için hacim verisi çekilirken hata: {e}")
            return None

if __name__ == "__main__":
    radar = TurnoverRadar()
    # Örnek test (Eğer gün içi açıksa THYAO vs test edilebilir, 15dk gecikmelidir)
    sonuc = radar.check_turnover("THYAO", 1_380_000_000) # THYAO örnek halka açıklık lotu
    print(sonuc)
