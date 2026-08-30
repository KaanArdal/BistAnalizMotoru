import requests
import sys
import config

sys.stdout.reconfigure(encoding='utf-8')

def send_telegram_message(message: str):
    """
    Gönderilen mesajı Telegram üzerinden belirtilen Chat ID'ye iletir.
    """
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("Telegram kimlik bilgileri eksik, mesaj gönderilemedi:", message)
        return False

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram mesajı başarıyla gönderildi.")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Telegram API Hatası: {e.response.text}")
        return False
    except Exception as e:
        print(f"Telegram mesajı gönderilirken genel hata oluştu: {e}")
        return False

if __name__ == "__main__":
    # Test amaçlı
    send_telegram_message("🤖 <b>BIST & Halka Arz Analiz Motoru</b> başlatıldı!\nSinyaller buraya düşecek.")
