import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from kap_scraper import KAPScraper
from izahname_analyzer import IzahnameAnalyzer
from turnover_radar import TurnoverRadar
from portfolio_manager import PortfolioManager

scraper = KAPScraper()
analyzer = IzahnameAnalyzer()
radar = TurnoverRadar()
portfolio = PortfolioManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "🤖 **BIST Analiz Motoruna Hoş Geldin!**\n\n"
        "GİRİŞ (ALIM) STRATEJİSİ:\n"
        "/son - En son eklenen halka arzı analiz eder.\n"
        "/analiz <KOD> - İstediğin bir halka arzı (Örn: /analiz KOTON) analiz eder.\n"
        "/hepsi - Yakın zamandaki tüm halka arzların listesini getirir.\n\n"
        "ÇIKIŞ (SATIM) STRATEJİSİ:\n"
        "/radar - Aktif işlem gören halka arzlarda 'Balina Çıkışı' (El Değiştirme Oranı) kontrolü yapar."
    )
    await update.message.reply_text(mesaj, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "🤖 **BIST Analiz Motoru - Komut Rehberi**\n\n"
        "📖 **GENEL KOMUTLAR**\n"
        "/start - Botu başlatır ve kısa bilgi verir.\n"
        "/help - Bu yardım menüsünü gösterir.\n"
        "/son - En son eklenen halka arzı otomatik bulup analiz eder.\n"
        "/analiz <KOD> - İstediğiniz bir halka arzın detaylı yapay zeka analizini yapar (Örn: `/analiz KOTON`).\n"
        "/hepsi - Yakın zamanda onaylanan halka arzların listesini getirir.\n"
        "/radar - Portföydeki hisseler için anlık 'Balina Çıkışı' (el değiştirme oranı) taraması yapar.\n\n"
        "💼 **PORTFÖY KOMUTLARI**\n"
        "Yatırımlarınızı takip etmek için komutları kullanabilirsiniz:\n\n"
        "👉 **Hisse Ekleme (Alım):**\n"
        "`/[kullanıcı_adı] [lot] [kod] al [maliyet]`\n"
        "Örn: `/mehmet 50 netgl al 15.50`\n\n"
        "👉 **Hisse Satma:**\n"
        "`/[kullanıcı_adı] [lot] [kod] sat`\n"
        "Örn: `/mehmet 30 netgl sat`\n\n"
        "👉 **Kişisel Portföy:**\n"
        "`/[kullanıcı_adı]` - Sadece o kişiye ait yatırımları ve kâr/zarar durumunu gösterir. (Örn: `/mehmet`)\n\n"
        "👉 **Grup Portföyü:**\n"
        "/kisiler - Botu kullanan herkesin yatırımlarını ve güncel durumlarını listeler."
    )
    await update.message.reply_text(mesaj, parse_mode="Markdown")

async def son_halka_arz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ En son halka arz taranıyor, lütfen bekleyin...")
    raw_text = scraper.get_latest_ipo_text()
    if not raw_text:
        await update.message.reply_text("❌ Halka arz verisi çekilemedi.")
        return
    
    await update.message.reply_text("🧠 Yapay zeka izahnameyi analiz ediyor...")
    rapor = analyzer.analyze_halka_arz(raw_text)
    await update.message.reply_text(rapor)

async def analiz_et(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Lütfen bir hisse kodu girin. Örn: `/analiz KOTON`", parse_mode="Markdown")
        return
        
    kodu = context.args[0].upper()
    await update.message.reply_text(f"⏳ {kodu} için veriler taranıyor...")
    
    raw_text = scraper.search_ipo_text(kodu)
    if not raw_text:
        await update.message.reply_text(f"❌ {kodu} kodlu halka arz bulunamadı. Kodun doğruluğundan emin olun.")
        return
        
    await update.message.reply_text("🧠 Yapay zeka izahnameyi analiz ediyor...")
    rapor = analyzer.analyze_halka_arz(raw_text)
    await update.message.reply_text(rapor)

async def hepsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Son halka arzlar listeleniyor...")
    liste = scraper.get_all_recent_ipos()
    if not liste:
        await update.message.reply_text("Liste çekilemedi.")
        return
        
    mesaj = "📋 **Son Halka Arzlar:**\n\n"
    for item in liste:
        mesaj += f"🔹 {item['isim']} ({item['kod']})\n"
        
    mesaj += "\nDetaylı analiz için `/analiz KOD` yazabilirsiniz."
    await update.message.reply_text(mesaj, parse_mode="Markdown")

async def kisiler_portfoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not portfolio.data:
        await update.message.reply_text("Henüz kimsenin portföyünde hisse yok.")
        return
        
    await update.message.reply_text("⏳ Tüm yatırımlar ve güncel fiyatlar çekiliyor...")
    mesaj = "👥 **TÜM KİŞİLERİN YATIRIMLARI:**\n\n"
    
    fiyat_cache = {}
    
    for username, hisseler in portfolio.data.items():
        mesaj += f"👤 **{username.capitalize()}:**\n"
        user_toplam = 0
        
        for kod, info in hisseler.items():
            lot = info['lot']
            maliyet = info['maliyet']
            
            if kod not in fiyat_cache:
                fiyat_cache[kod] = portfolio.get_current_price(kod)
                
            current_price = fiyat_cache[kod]
            if current_price:
                guncel_deger = current_price * lot
                maliyet_deger = maliyet * lot
                user_toplam += guncel_deger
                mesaj += f"  - {kod}: {lot} Lot ({maliyet_deger:.2f} TL -> {guncel_deger:.2f} TL)\n"
            else:
                mesaj += f"  - {kod}: {lot} Lot (Fiyat Yok)\n"
                
        mesaj += f"  *Toplam:* {user_toplam:.2f} TL\n\n"
        
    await update.message.reply_text(mesaj, parse_mode="Markdown")

async def handle_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.startswith('/'):
        return
        
    parts = text[1:].split()
    if not parts:
        return
        
    komut = parts[0].lower()
    
    if komut in ['start', 'son', 'analiz', 'hepsi', 'radar', 'kisiler', 'help']:
        return
        
    if len(parts) >= 4 and parts[3].lower() in ['al', 'sat']:
        try:
            username = komut
            lot = int(parts[1])
            kod = parts[2].upper()
            islem_tipi = parts[3].lower()
            fiyat = float(parts[4]) if len(parts) > 4 else None
            
            yeni_lot = portfolio.islem_yap(username, lot, kod, islem_tipi, fiyat)
            
            if islem_tipi == "al":
                await update.message.reply_text(f"✅ {username.capitalize()} portföyüne {lot} lot {kod} eklendi. Toplam lot: {yeni_lot}")
            else:
                if yeni_lot == 0:
                    await update.message.reply_text(f"✅ {username.capitalize()} portföyündeki tüm {kod} lotları satıldı.")
                else:
                    current_price = portfolio.get_current_price(kod)
                    if current_price:
                        kalan_deger = current_price * yeni_lot
                        await update.message.reply_text(f"✅ {username.capitalize()} portföyünden {lot} lot {kod} satıldı. Kalan {yeni_lot} lotun güncel değeri yaklaşık: {kalan_deger:.2f} TL")
                    else:
                        await update.message.reply_text(f"✅ {username.capitalize()} portföyünden {lot} lot {kod} satıldı. Kalan lot: {yeni_lot}")
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {str(e)}")
            
    elif len(parts) == 1:
        username = komut
        if username not in portfolio.data:
            await update.message.reply_text(f"❌ '{username}' adlı kullanıcının portföyünde hisse bulunamadı. (Kayıt eklemek için: `/{username} 50 NETGL al 15.50`)", parse_mode="Markdown")
            return
            
        await update.message.reply_text(f"⏳ {username.capitalize()} için güncel fiyatlar hesaplanıyor...")
        mesaj = f"👤 **{username.capitalize()} Portföyü:**\n\n"
        toplam_portfoy_degeri = 0
        
        for kod, info in portfolio.data[username].items():
            lot = info['lot']
            maliyet = info['maliyet']
            current_price = portfolio.get_current_price(kod)
            
            if current_price:
                guncel_deger = current_price * lot
                maliyet_deger = maliyet * lot
                kar_zarar = guncel_deger - maliyet_deger
                toplam_portfoy_degeri += guncel_deger
                mesaj += f"🔹 **{kod}**: {lot} Lot\n"
                mesaj += f"   Maliyet: {maliyet:.2f} TL | Güncel Fiyat: {current_price:.2f} TL\n"
                mesaj += f"   Değer: {guncel_deger:.2f} TL (Kâr/Zarar: {kar_zarar:.2f} TL)\n\n"
            else:
                mesaj += f"🔹 **{kod}**: {lot} Lot (Fiyat çekilemedi)\n\n"
                
        mesaj += f"💰 **Toplam Portföy Değeri:** {toplam_portfoy_degeri:.2f} TL"
        await update.message.reply_text(mesaj, parse_mode="Markdown")

async def radar_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 El değiştirme radarı taramaya başladı...")
    takip_listesi = scraper.get_active_ipos()
    portfoydeki_hisseler = portfolio.get_all_active_tickers()
    
    mesaj = "🚨 **EL DEĞİŞTİRME RADARI** 🚨\n\n"
    uyari_var_mi = False
    kontrol_edilen_var_mi = False
    
    for hisse in takip_listesi:
        if hisse["kodu"] in portfoydeki_hisseler:
            kontrol_edilen_var_mi = True
            sonuc = radar.check_turnover(hisse["kodu"], hisse["lot"])
            if sonuc:
                mesaj += f"🔹 **{sonuc['hisse_kodu']}**\n"
                mesaj += f"Hacim: {sonuc['gunluk_hacim']:,} Lot\n"
                mesaj += f"El Değiştirme: %{sonuc['el_degistirme_orani']}\n"
                if sonuc['uyari']:
                    mesaj += "⚠️ **DİKKAT! Balina Çıkışı Olabilir! (Eşik aşıldı)**\n\n"
                    uyari_var_mi = True
                else:
                    mesaj += "✅ Güvenli Bölgede (Tavan serisi devam edebilir)\n\n"
                
    if not kontrol_edilen_var_mi:
        await update.message.reply_text("Şu an portföylerde olan ve radara takılan yeni halka arz bulunmuyor.")
        return
        
    if not uyari_var_mi:
        mesaj += "\nŞu an için radara yakalanan kritik bir satış baskısı yok. Hisselerde tutunmaya devam edilebilir."
        
    await update.message.reply_text(mesaj, parse_mode="Markdown")

async def radar_job(context: ContextTypes.DEFAULT_TYPE):
    """Arka planda sürekli radarı kontrol eden JobQueue görevi."""
    try:
        print("Arka plan radarı çalışıyor...")
        takip_listesi = scraper.get_active_ipos()
        portfoydeki_hisseler = portfolio.get_all_active_tickers()
        
        for hisse in takip_listesi:
            if hisse["kodu"] in portfoydeki_hisseler:
                sonuc = radar.check_turnover(hisse["kodu"], hisse["lot"])
                if sonuc and sonuc['uyari']:
                    mesaj = f"🚨 **OTOMATİK RADAR UYARISI** 🚨\n\n**{sonuc['hisse_kodu']}** hissesinde günlük el değiştirme oranı %{sonuc['el_degistirme_orani']} seviyesine ulaştı!\n\nKurumsal yatırımcı veya balina çıkışı başlamış olabilir. Tavanın bozulma riski çok yüksek, çıkış (satış) stratejinizi gözden geçirin!"
                    await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=mesaj, parse_mode="Markdown")
    except Exception as e:
        print(f"Arka plan radar hatası: {e}")

async def new_ipo_alert_job(context: ContextTypes.DEFAULT_TYPE):
    """Arka planda yeni eklenen halka arzları kontrol eder."""
    try:
        liste = scraper.get_all_recent_ipos()
        if not liste:
            return
            
        en_yeni_kod = liste[0]["kod"]
        
        # Son bilinen halka arzı dosyadan oku
        last_ipo_file = "last_ipo.txt"
        son_bilinen = ""
        import os
        if os.path.exists(last_ipo_file):
            with open(last_ipo_file, "r", encoding="utf-8") as f:
                son_bilinen = f.read().strip()
                
        if en_yeni_kod != son_bilinen and en_yeni_kod != "BİLİNMİYOR":
            # Yeni halka arz bulundu!
            with open(last_ipo_file, "w", encoding="utf-8") as f:
                f.write(en_yeni_kod)
                
            # İlk çalışmada bildirim atmamak için son_bilinen boşsa sadece kaydet
            if son_bilinen != "":
                isim = liste[0]["isim"]
                mesaj = f"🔥 **YENİ HALKA ARZ TESPİT EDİLDİ!** 🔥\n\n📌 **Şirket:** {isim}\n🔖 **Kod:** {en_yeni_kod}\n\nDetaylı analizini anında görmek için hemen şu komutu yazabilirsiniz:\n👉 `/analiz {en_yeni_kod}`"
                await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=mesaj, parse_mode="Markdown")
                
    except Exception as e:
        print(f"Yeni halka arz kontrol hatası: {e}")

def main():
    if not config.TELEGRAM_BOT_TOKEN:
        print("Telegram Token eksik!")
        return

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("son", son_halka_arz))
    application.add_handler(CommandHandler("analiz", analiz_et))
    application.add_handler(CommandHandler("hepsi", hepsi))
    application.add_handler(CommandHandler("radar", radar_kontrol))
    application.add_handler(CommandHandler("kisiler", kisiler_portfoy))
    application.add_handler(MessageHandler(filters.COMMAND, handle_custom_command))
    
    # Arka plan görevini JobQueue ile ayarla
    application.job_queue.run_repeating(radar_job, interval=3600, first=10) # 1 Saatte bir balina çıkışı kontrolü
    application.job_queue.run_repeating(new_ipo_alert_job, interval=7200, first=20) # 2 Saatte bir yeni arz kontrolü

    print("Telegram dinleyicisi ve Radar başlatıldı. Mesajlar bekleniyor...")
    application.run_polling()

if __name__ == "__main__":
    main()
