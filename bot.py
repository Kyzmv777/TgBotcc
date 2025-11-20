import logging
import sqlite3
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot Configuration - Environment variables kullan
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8565098842:AAEx53sbeD0d90u9-e6CbVs8sPJZL0G99oc')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '7630138416'))
SUPPORT_USERNAME = "@hunterdarkweb"

# Payment Links
PAYMENT_LINKS = {
    "2D CC Shop": "https://nowpayments.io/payment/?iid=5569983905",
    "3D OTP Shop": "https://nowpayments.io/payment/?iid=5009457698",
    "NFC Shop": "https://nowpayments.io/payment/?iid=4525469733",
    "Booking Virtual CC": "https://nowpayments.io/payment/?iid=4938689190",
    "EVM2X Dumpler": "https://nowpayments.io/payment/?iid=5217281645", 
    "MSRX Dumpler": "https://nowpayments.io/payment/?iid=4586948395",
    "Balance Checker": "https://nowpayments.io/payment/?iid=6040790411",
    "Crypto Phishing System": "https://nowpayments.io/payment/?iid=5063318511",
    "2D 3D NFC OTP Phishing": "https://nowpayments.io/payment/?iid=6205350637"
}

# Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def init_db():
    conn = sqlite3.connect('/tmp/hunterdark.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT,
                  product_name TEXT, price_usd REAL, payment_status TEXT, 
                  order_date TEXT, delivered INTEGER DEFAULT 0, category TEXT)''')
    conn.commit()
    conn.close()
    print("✅ Database hazır")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome_text = f"""🕶️ **HUNTER DARK WEB TEAM** 🕶️

👤 **User:** {user.first_name}
🆔 **ID:** {user.id}

💎 **Premium Products:**

• 💳 2D CC Shop - 25 USDT
• 🔐 3D OTP Shop - 80 USDT  
• 📱 NFC Shop - 230 USDT
• 🏨 Booking VCC - 30 USDT
• ⚡ EVM2X Dumpler - 700 USDT
• 💾 MSRX Dumpler - 540 USDT
• 📊 Balance Checker - 50 USDT
• 🎣 Crypto Phishing - 3000 USDT
• 🌐 Full Phishing Kit - 1500 USDT

👇 *Kategori seçin:*"""
    
    keyboard = [
        [InlineKeyboardButton("💳 2D CC Shop (25 USDT)", callback_data="cat_2D CC Shop")],
        [InlineKeyboardButton("🔐 3D OTP Shop (80 USDT)", callback_data="cat_3D OTP Shop")],
        [InlineKeyboardButton("📱 NFC Shop (230 USDT)", callback_data="cat_NFC Shop")],
        [InlineKeyboardButton("🏨 Booking VCC (30 USDT)", callback_data="cat_Booking Virtual CC")],
        [InlineKeyboardButton("⚡ EVM2X Dumpler (700 USDT)", callback_data="cat_EVM2X Dumpler")],
        [InlineKeyboardButton("💾 MSRX Dumpler (540 USDT)", callback_data="cat_MSRX Dumpler")],
        [InlineKeyboardButton("📊 Balance Checker (50 USDT)", callback_data="cat_Balance Checker")],
        [InlineKeyboardButton("🎣 Crypto Phishing (3000 USDT)", callback_data="cat_Crypto Phishing System")],
        [InlineKeyboardButton("🌐 Full Phishing Kit (1500 USDT)", callback_data="cat_2D 3D NFC OTP Phishing")],
        [InlineKeyboardButton("👨‍💻 Support", callback_data="support")]
    ]
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "support":
        await query.edit_message_text(f"👨‍💻 **Support:** {SUPPORT_USERNAME}")
        return
        
    if query.data == "main_menu":
        await start(update, context)
        return
        
    if query.data.startswith("cat_"):
        category = query.data.replace("cat_", "")
        prices = {
            "2D CC Shop": 25, "3D OTP Shop": 80, "NFC Shop": 230,
            "Booking Virtual CC": 30, "EVM2X Dumpler": 700, "MSRX Dumpler": 540,
            "Balance Checker": 50, "Crypto Phishing System": 3000,
            "2D 3D NFC OTP Phishing": 1500
        }
        
        price = prices.get(category, 0)
        user_id = query.from_user.id
        username = query.from_user.username or "NoUsername"
        
        conn = sqlite3.connect('/tmp/hunterdark.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''INSERT INTO orders (user_id, username, product_name, price_usd, payment_status, order_date, category) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (user_id, username, category, price, "pending", datetime.now().isoformat(), category))
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        
        payment_link = PAYMENT_LINKS.get(category, "#")
        
        payment_text = f"""💳 **SİPARİŞ #HD{order_id:06d}**

🛍️ **Ürün:** {category}
💰 **Tutar:** {price} USDT
👤 **Müşteri:** @{username}

💳 **Ödeme Talimatları:**

1. **🌐 Pay Now** butonuna tıklayın
2. NowPayments'ta ödemeyi tamamlayın
3. **✅ I've Paid** butonuna tıklayın
4. 1-12 saat içinde teslimat"""
        
        keyboard = [
            [InlineKeyboardButton("🌐 Pay Now", url=payment_link)],
            [InlineKeyboardButton("✅ I've Paid", callback_data=f"confirm_{order_id}")],
            [InlineKeyboardButton("📞 Support", callback_data="support")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(payment_text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith("confirm_"):
        order_id = int(query.data.replace("confirm_", ""))
        
        support_text = f"""✅ **ÖDEME ONAYI ALINDI**

📦 **Sipariş ID:** HD{order_id:06d}

{SUPPORT_USERNAME} ile iletişime geçin."""
        
        keyboard = [
            [InlineKeyboardButton("📞 Support", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(support_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def deliver_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Yetkiniz yok.")
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: /deliver <sipariş_id>")
        return
    
    try:
        order_id = int(context.args[0])
        conn = sqlite3.connect('/tmp/hunterdark.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT user_id, category FROM orders WHERE id = ?", (order_id,))
        order = c.fetchone()
        
        if order:
            user_id, category = order
            product_content = f"""🕶️ **HUNTER DARK WEB TEAM** 🕶️

📦 **SİPARİŞ HD{order_id:06d} TESLİM EDİLDİ**

Ürün: {category}
Sipariş ID: HD{order_id:06d}

{SUPPORT_USERNAME} ile iletişime geçin.

Teşekkür ederiz! 🚀"""
            
            await context.bot.send_message(chat_id=user_id, text=product_content)
            await update.message.reply_text(f"✅ HD{order_id:06d} teslim edildi")
        else:
            await update.message.reply_text("❌ Sipariş bulunamadı")
            
        conn.close()
            
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")

def main():
    print("🕶️ Hunter Dark Bot başlatılıyor...")
    init_db()
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Handler'ları ekle
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("deliver", deliver_product))
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        print("✅ Bot başarıyla başlatıldı!")
        print("🚀 Render.com'da çalışıyor...")
        print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
        
        # Polling başlat
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Bot başlatılamadı: {e}")

if __name__ == "__main__":
    main()