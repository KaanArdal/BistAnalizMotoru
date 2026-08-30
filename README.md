# BIST Halka Arz & Analiz Motoru 🚀 (Telegram Bot Edition)

Borsa İstanbul'daki halka arzları (IPO) ve yeni işlem görmeye başlayan hisseleri tamamen otonom bir şekilde analiz eden, "akıllı parayı" takip eden ve Telegram üzerinden etkileşimli çalışan bir Yatırım Asistanı.

## 🌟 Neler Yapabiliyor?

### 1. NLP İzahname Analizi (Giriş Stratejisi)
Google Gemini AI gücünü kullanarak, halka arz olan şirketlerin resmi izahnamelerini (Fon Kullanım Yeri) saniyeler içinde okur ve sana şirketin borç mu kapatacağını yoksa yatırım mı yapacağını özetler. 
- 🟢 **KESİN KATIL:** Şirket parayı yatırıma ve teknolojiye ayırıyorsa.
- 🔴 **UZAK DUR:** Paranın çoğu kısa vadeli borçları kapatmaya gidiyorsa.

### 2. Balina (Turnover) Radarı (Çıkış Stratejisi) 🐳
"Halka arza girdim, tavan bozduğunda ne zaman satacağım?" stresine son!
Bot, arka planda (saat başı) `yfinance` üzerinden tahtadaki günlük el değiştirme oranını takip eder. Eğer kurumsallar veya balinalar mallarını boşaltmaya başlarsa (Örn: %15 hacim sınırı aşılırsa) Telegram'dan sana acil durum sat sinyali (**🚨 DİKKAT! Balina Çıkışı Olabilir!**) gönderir.

### 3. Yeni Halka Arz Dedektörü
Senin piyasayı takip etmene gerek yok! Bot her 2 saatte bir `halkarz.com` verilerini tarar. Yeni bir şirket halka arz açıklandığı an, doğrudan cebine **"🔥 YENİ HALKA ARZ TESPİT EDİLDİ!"** bildirimi gönderir.

## 🤖 Telegram Komutları

Botla Telegram üzerinden direkt mesajlaşarak tüm analizleri anlık olarak çekebilirsiniz:

- **`/hepsi`** : En son açıklanan 10 halka arzı listeler.
- **`/analiz KOD`** : İstediğiniz bir hissenin (Örn: `/analiz INTET`) izahnamesini anında yapay zekaya okutur ve sana özet raporu çıkartır.
- **`/son`** : Açıklanan en son halka arzı otomatik bulup analiz eder.
- **`/radar`** : Aktif işlem gören hisselerin o anki hacimlerini (El Değiştirme oranlarını) anlık tarar ve balina çıkışı olup olmadığını raporlar.

## ⚙️ Kurulum & Çalıştırma

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
2. Klasördeki `.env.example` dosyasının adını `.env` olarak değiştirin ve içine kendi API bilgilerinizi girin:
   - `TELEGRAM_BOT_TOKEN`: BotFather üzerinden alınan Telegram token'ı.
   - `TELEGRAM_CHAT_ID`: Mesajın gönderileceği sizin kişisel sohbet ID'niz.
   - `GEMINI_API_KEY`: Google AI Studio'dan alınan yapay zeka anahtarı.

3. Bot sunucusunu başlatın:
   ```bash
   python bot_server.py
   ```
*Not: Bot çalıştığı sürece arka planda hem yeni arzları takip edecek hem de balina çıkışları için nöbet tutacaktır.*

## ⚠️ Yasal Uyarı
Bu proje tamamen eğitim ve kişisel analiz amaçlı kodlanmıştır. İçerisindeki yapay zeka yorumları veya radar sinyalleri kesinlikle **Yatırım Tavsiyesi Değildir (YTD)**. 
