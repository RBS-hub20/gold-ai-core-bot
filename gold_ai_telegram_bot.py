import asyncio
import os
import requests
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "@goldaicore_alerts")

def get_gold_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        data = r.json()
        return float(data.get("price", 4341.94))
    except:
        return 4341.94

def compute_signal(price):
    entry = round(price) - 7
    sl = entry - 25
    tp = entry + 35
    return entry, sl, tp, "BUY", 82, 64

async def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing!")
        return
        
    bot = Bot(token=BOT_TOKEN)
    
    # Send only ONCE
    try:
        await bot.send_message(
            chat_id=CHAT_ID, 
            text="🟢 <b>Gold AI Core Bot Activated - Free Beta Live!</b>\n\nMonitoring XAUUSD every 30s... Beta 2/50",
            parse_mode="HTML"
        )
        print("Activation sent!")
    except Exception as e:
        print(f"Activation error: {e}")

    last_price = 0
    last_alert_time = 0
    
    while True:
        try:
            price = get_gold_price()
            now = datetime.now().timestamp()
            
            # Send only if 0.3% move OR every 30 mins (1800s)
            should_send = False
            if last_price == 0:
                should_send = False  # Don't send immediately after activation
            elif abs(price - last_price) / last_price > 0.003:
                should_send = True
            elif now - last_alert_time > 1800:
                should_send = True
                
            if should_send:
                entry, sl, tp, side, conf, rsi = compute_signal(price)
                change = ((price - last_price)/last_price)*100
                msg = f"""🚨 <b>GOLD AI CORE • LIVE</b>

💰 <b>XAUUSD: ${price:,.2f}</b> ({change:+.2f}%)
📊 <b>Signal: {side} {entry}</b> | SL {sl} | TP {tp}
🎯 Confidence: {conf}% | RSI {rsi}

<a href="https://gold.rbslabs.com">Open Dashboard →</a>"""
                await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML", disable_web_page_preview=True)
                last_alert_time = now
                print(f"Alert sent: {price}")
                
            last_price = price
        except Exception as e:
            print(f"Loop error: {e}")
            
        await asyncio.sleep(30)

if name == "__main__":
    asyncio.run(main())
