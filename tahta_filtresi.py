class TahtaFiltresi:
    def __init__(self):
        # Milyon TL cinsinden eşikler
        self.sig_tahta_limiti = 500_000_000      # 500 Milyon TL altı "Sığ"
        self.derin_tahta_limiti = 2_000_000_000    # 2 Milyar TL üstü "Derin"

    def analyze_tahta(self, hisse_kodu, arz_fiyati, arz_edilen_lot):
        """
        Halka arz edilen kısmın toplam büyüklüğünü hesaplar ve tahta tipini belirler.
        """
        toplam_buyukluk = arz_fiyati * arz_edilen_lot
        
        tahta_tipi = "Orta Boy Tahta"
        risk_durumu = "Dengeli"
        
        if toplam_buyukluk < self.sig_tahta_limiti:
            tahta_tipi = "Sığ Tahta"
            risk_durumu = "⚠️ Manipülasyona çok açık, hızlı tavan serisi potansiyeli yüksek ama riskli."
        elif toplam_buyukluk > self.derin_tahta_limiti:
            tahta_tipi = "Derin Tahta"
            risk_durumu = "🛡️ Kurumsal ağırlıklı, daha stabil, kolay kolay tavan bozup çakılmaz."
            
        buyukluk_milyon_tl = toplam_buyukluk / 1_000_000
            
        return {
            "hisse_kodu": hisse_kodu,
            "toplam_buyukluk_milyon_tl": round(buyukluk_milyon_tl, 2),
            "tahta_tipi": tahta_tipi,
            "risk_durumu": risk_durumu
        }

if __name__ == "__main__":
    filtre = TahtaFiltresi()
    sonuc = filtre.analyze_tahta("TEST", 25.50, 15_000_000)
    print(sonuc)
