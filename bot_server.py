import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from kap_scraper import KAPScraper
from izahname_analyzer import IzahnameAnalyzer
from turnover_radar import TurnoverRadar

scraper = KAPScraper()
analyzer = IzahnameAnalyzer()
radar = TurnoverRadar()

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

async def radar_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 El değiştirme radarı taramaya başladı...")
    takip_listesi = scraper.get_active_ipos()
    
    mesaj = "🚨 **EL DEĞİŞTİRME RADARI** 🚨\n\n"
    uyari_var_mi = False
    
    for hisse in takip_listesi:
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
                
    if not uyari_var_mi:
        mesaj += "\nŞu an için radara yakalanan kritik bir satış baskısı yok. Hisselerde tutunmaya devam edilebilir."
        
    await update.message.reply_text(mesaj, parse_mode="Markdown")

async def radar_job(context: ContextTypes.DEFAULT_TYPE):
    """Arka planda sürekli radarı kontrol eden JobQueue görevi."""
    try:
        print("Arka plan radarı çalışıyor...")
        takip_listesi = scraper.get_active_ipos()
        for hisse in takip_listesi:
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
    application.add_handler(CommandHandler("son", son_halka_arz))
    application.add_handler(CommandHandler("analiz", analiz_et))
    application.add_handler(CommandHandler("hepsi", hepsi))
    application.add_handler(CommandHandler("radar", radar_kontrol))
    
    # Arka plan görevini JobQueue ile ayarla
    application.job_queue.run_repeating(radar_job, interval=3600, first=10) # 1 Saatte bir balina çıkışı kontrolü
    application.job_queue.run_repeating(new_ipo_alert_job, interval=7200, first=20) # 2 Saatte bir yeni arz kontrolü

    print("Telegram dinleyicisi ve Radar başlatıldı. Mesajlar bekleniyor...")
    application.run_polling()

if __name__ == "__main__":
    main()
