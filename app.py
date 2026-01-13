import os
import requests
from flask import Flask
import threading
import time
import logging

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8353596700:AAGGBzOlnQZepaq0lnXys4KlQNKozJpXq7A")
CHAT_ID = os.environ.get("CHAT_ID", "5316017487")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

monitor_running = False

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
        requests.post(url, data=payload, timeout=5)
        return True
    except:
        return False

def simple_parse():
    """Простой тестовый парсинг"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Пробуем получить страницу
        urls = [
            "https://funpay.com/chips/186/",
            "https://funpay.com/lots/1442/"
        ]
        
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                logger.info(f"URL: {url}, Status: {response.status_code}")
                
                # Простая проверка - ищем слово "руб" в ответе
                if 'руб' in response.text.lower():
                    return "Найдены товары с ценами"
                    
            except Exception as e:
                logger.error(f"Error: {e}")
        
        return "Парсинг завершен"
        
    except Exception as e:
        return f"Ошибка: {e}"

def monitor():
    global monitor_running
    
    logger.info("🚀 Мониторинг запущен")
    send_telegram("🤖 <b>FunPay Hunter v2 запущен!</b>")
    
    check_count = 0
    
    while monitor_running:
        try:
            check_count += 1
            logger.info(f"🔍 Проверка #{check_count}")
            
            # Делаем простой парсинг
            result = simple_parse()
            
            # Отправляем статус
            message = f"✅ Проверка #{check_count}\nРезультат: {result}"
            send_telegram(message)
            
            # Ждем 5 минут
            for i in range(30):
                if not monitor_running:
                    break
                time.sleep(10)  # 10 сек * 30 = 5 минут
                
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(60)
    
    logger.info("🛑 Мониторинг остановлен")

@app.route('/')
def home():
    return """
    <h1>🤖 FunPay Hunter v2</h1>
    <p><a href="/start">▶️ Запустить</a> | <a href="/stop">⏹️ Остановить</a></p>
    <p><a href="/test">🧪 Тест</a> | <a href="/health">❤️ Health</a></p>
    """

@app.route('/start')
def start():
    global monitor_running
    if not monitor_running:
        monitor_running = True
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return "✅ Мониторинг запущен"
    return "⚠️ Уже запущен"

@app.route('/stop')
def stop():
    global monitor_running
    monitor_running = False
    return "⏹️ Остановлен"

@app.route('/test')
def test():
    result = simple_parse()
    return f"<h1>Тест парсинга</h1><p>{result}</p>"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
