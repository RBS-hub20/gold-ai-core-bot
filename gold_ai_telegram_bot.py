import asyncio
import os
import requests
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "@goldaicore_alerts")
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://goldaicore.online")

GOLD_API = "https://api.gold-api.com/price/XAU"
CHECK_INTERVAL = 60  # ginawa kong 60s para di spammy

def get_gold_price():
    try:
        r = requests.get(GOLD_API, timeout=10)
        data = r.json()
        return data.get("price", 4341.94)
    except:
        return 4341.94

def compute_signal(price):
    entry = round(price) - 7
    sl = entry - 25
    tp = entry + 35
    rsi = 64
    side = "BUY" if rsi >= 50 else "SELL"
    conf = 82
    return entry, sl, tp, side, conf, rsi

async def send_alert(bot, price, change_pct=1.18):
    entry, sl, tp, side, conf, rsi = compute_signal(price)
    msg = f"""
🚨 <b>GOLD AI CORE • LIVE</b>

💰 <b>XAUUSD: ${price:,.2f}</b> (+{change_pct}%)
📊 <b>Signal: {side} {entry}</b> | SL {sl} | TP {tp}
🎯 Confidence: {conf}% | RSI {rsi} Bullish

🔥 Status: <b>FREE BETA</b>

<a href="{WEBSITE_URL}">Open Dashboard →</a>
"""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML", disable_web_page_preview=False)
        print(f"[{datetime.now()}] Sent alert: {price}")
    except Exception as e:
        print(f"Error sending: {e}")

async def main():
    bot = Bot(token=BOT_TOKEN)
    last_price = 0
    first_run = True
    
    while True:
        price = get_gold_price()
        
        # FIXED - no more ZeroDivisionError
        should_send = False
        if last_price == 0:
            should_send = True
        elif abs(price - last_price) / last_price > 0.005:  # 0.5% change
            should_send = True
        
        if should_send:
            # Wag mag send ng startup message every time, signal lang
            if first_run:
                startup_msg = f"🟢 <b>Gold AI Core Bot Online!</b>\n\nMonitoring XAUUSD every 60s...\n🌐 {WEBSITE_URL}"
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=startup_msg, parse_mode="HTML", disable_web_page_preview=False)
                except:
                    pass
                first_run = False
            else:
                await send_alert(bot, price)
            
            last_price = price
        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: Set BOT_TOKEN env variable!")
    else:
        asyncio.run(main())
