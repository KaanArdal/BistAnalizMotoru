import json
import os
import yfinance as yf

class PortfolioManager:
    def __init__(self, filename="portfolio.json"):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_data(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def islem_yap(self, username, lot, kod, islem_tipi, fiyat=None):
        """
        islem_tipi: 'al' veya 'sat'
        """
        username = username.lower()
        kod = kod.upper()
        
        if username not in self.data:
            self.data[username] = {}

        if kod not in self.data[username]:
            self.data[username][kod] = {"lot": 0, "maliyet": 0.0}

        mevcut_lot = self.data[username][kod]["lot"]
        mevcut_maliyet = self.data[username][kod]["maliyet"]

        if islem_tipi == "al":
            if fiyat is None:
                raise ValueError("Alım işleminde fiyat (ilk fiyat) belirtilmelidir!")
            
            yeni_lot = mevcut_lot + lot
            toplam_maliyet = (mevcut_lot * mevcut_maliyet) + (lot * fiyat)
            yeni_maliyet = toplam_maliyet / yeni_lot if yeni_lot > 0 else 0
            
            self.data[username][kod]["lot"] = yeni_lot
            self.data[username][kod]["maliyet"] = yeni_maliyet
            self.save_data()
            return yeni_lot

        elif islem_tipi == "sat":
            if lot > mevcut_lot:
                raise ValueError(f"Yeterli lot yok! Mevcut lot: {mevcut_lot}")
                
            yeni_lot = mevcut_lot - lot
            if yeni_lot == 0:
                del self.data[username][kod]
                if not self.data[username]:
                    del self.data[username]
            else:
                self.data[username][kod]["lot"] = yeni_lot
                
            self.save_data()
            return yeni_lot

        else:
            raise ValueError("Bilinmeyen işlem tipi. 'al' veya 'sat' kullanın.")

    def get_current_price(self, kod):
        try:
            ticker = yf.Ticker(f"{kod}.IS")
            data = ticker.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except Exception:
            pass
        return None

    def get_all_active_tickers(self):
        tickers = set()
        for user_data in self.data.values():
            for kod in user_data.keys():
                tickers.add(kod)
        return list(tickers)
