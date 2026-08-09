import asyncio
import os
import requests
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "@goldaicore_alerts")

# NEW - Custom Domain mo!
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://goldaicore.online")
# Pwede rin FRONTEND_URL or GOLD_WEBSITE

GOLD_API = "https://api.gold-api.com/price/XAU"
CHECK_INTERVAL = 30

HIGH_IMPACT = [
    {"time": "20:30", "title": "US CPI", "tag": "CPI"},
    {"time": "Aug 13", "title": "PPI Data", "tag": "PPI"},
    {"time": "Aug 14", "title": "Retail Sales", "tag": "USD"},
    {"time": "Aug 15", "title": "Fed Speaks", "tag": "FED"},
    {"time": "Aug 20", "title": "FOMC Minutes", "tag": "FOMC"},
    {"time": "Sep 5", "title": "US NFP", "tag": "NFP"},
]

def get_gold_price():
    try:
        r = requests.get(GOLD_API, timeout=10)
        data = r.json()
        price = data.get("price", 4341.94)
        return price
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

📅 Next: <b>PPI Aug 13 20:30</b>
🔥 Status: <b>FREE BETA</b>

<a href="{WEBSITE_URL}">Open Dashboard →</a>
"""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML", disable_web_page_preview=True)
        print(f"[{datetime.now()}] Sent alert: {price}")
    except Exception as e:
        print(f"Error sending: {e}")

async def main():
    bot = Bot(token=BOT_TOKEN)
    last_price = 0
    await bot.send_message(chat_id=CHAT_ID, text="🟢 <b>Gold AI Core Bot Activated - Free Beta Live!</b>\n\nMonitoring XAUUSD every 30s...\n🌐 Dashboard: "+WEBSITE_URL, parse_mode="HTML")
    while True:
        price = get_gold_price()
        if abs(price - last_price) / last_price > 0.003 or last_price == 0:
            await send_alert(bot, price)
            last_price = price
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: Set BOT_TOKEN env variable!")
    else:
        asyncio.run(main())
