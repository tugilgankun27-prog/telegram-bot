import telebot
from telebot import types
import os, random

# ===== SOZLAMALAR =====
BOT_TOKEN = "6673316226:AAFqXnQqvz6pXegT8VLMQ3axck0SFN40RZ4"
ADMIN_CHAT_ID = 5272623103
BASE = "/sdcard/Download/birthday_bot/images"

STARS_PRICE = 10  # ⭐ 10 Stars

CARD_INFO = (
    "💳 KARTA ORQALI TO‘LOV\n\n"
    "🏦 Karta: HUMO / UZCARD\n"
    "🔢 Raqam: 4073420087931386 \n"
    "👤 Egasi: Abrorjon Urayimov\n\n"
    "📸 To‘lovdan so‘ng CHEKNI shu yerga yuboring."
)

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}
orders = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    name = m.from_user.first_name or "Do‘stimiz"
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🖼 Rasmli tabriklar")
    kb.add("📅 Tug‘ilgan kun qachon?")
    kb.add("📞 Kutilmagan qo‘ng‘iroq loyihasi")
    bot.send_message(
        m.chat.id,
        f"🎉 Assalomu alaykum, {name}!\nXush kelibsiz 😊",
        reply_markup=kb
    )

# ===== 12 TALIK =====
@bot.message_handler(func=lambda m: m.text == "🖼 Rasmli tabriklar")
def shablon_menu(m):
    user_state[m.chat.id] = "shablon"
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for i in range(1, 13):
        kb.add(str(i))
    kb.add("⬅️ Orqaga")
    bot.send_photo(
        m.chat.id,
        open(f"{BASE}/preview/shablon.png", "rb"),
        caption="🖼 Rasmli tabriklar\n🆓 1–2 bepul\n💳 Qolganlari pullik",
        reply_markup=kb
    )

# ===== 6 TALIK =====
@bot.message_handler(func=lambda m: m.text == "📅 Tug‘ilgan kun qachon?")
def birthday_menu(m):
    user_state[m.chat.id] = "birthday"
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for i in range(1, 7):
        kb.add(str(i))
    kb.add("⬅️ Orqaga")
    bot.send_photo(
        m.chat.id,
        open(f"{BASE}/preview/birthday.png", "rb"),
        caption="📅 Tug‘ilgan kun qachon?\n🆓 1–2 bepul\n💳 Qolganlari pullik",
        reply_markup=kb
    )

# ===== RAQAM TANLANGANDA =====
@bot.message_handler(func=lambda m: m.text.isdigit())
def handle_number(m):
    num = int(m.text)
    state = user_state.get(m.chat.id)

    if state == "shablon" and 1 <= num <= 12:
        if num <= 2:
            bot.send_photo(m.chat.id, open(f"{BASE}/shablon/{num}.png", "rb"))
        else:
            create_order(m, "12 talik rasm")
        return

    if state == "birthday" and 1 <= num <= 6:
        if num <= 2:
            bot.send_photo(m.chat.id, open(f"{BASE}/birthday/birthday{num}.png", "rb"))
        else:
            create_order(m, "6 talik rasm")
        return

# ===== BUYURTMA =====
def create_order(m, service):
    order_id = random.randint(10000, 99999)
    orders[order_id] = {"user": m.chat.id, "service": service}

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("⭐ Telegram Stars (10)", callback_data=f"stars_{order_id}"),
        types.InlineKeyboardButton("💳 Karta orqali", callback_data=f"card_{order_id}")
    )

    bot.send_message(
        m.chat.id,
        f"💳 To‘lov kerak\n📦 Xizmat: {service}\n🆔 Buyurtma: {order_id}",
        reply_markup=kb
    )

# ===== KARTA =====
@bot.callback_query_handler(func=lambda c: c.data.startswith("card_"))
def card_pay(c):
    bot.answer_callback_query(c.id)
    bot.send_message(c.message.chat.id, CARD_INFO)

# ===== STARS =====
@bot.callback_query_handler(func=lambda c: c.data.startswith("stars_"))
def stars_pay(c):
    prices = [types.LabeledPrice("Tug‘ilgan kun xizmati", STARS_PRICE)]
    bot.send_invoice(
        c.message.chat.id,
        title="🎉 Tug‘ilgan kun xizmati",
        description="Rasmli tabrik (Telegram Stars)",
        provider_token="",
        currency="XTR",
        prices=prices,
        payload="stars_payment"
    )

@bot.message_handler(content_types=['successful_payment'])
def stars_success(m):
    name = m.from_user.first_name or "Do‘stimiz"
    bot.send_message(
        m.chat.id,
        f"⭐ {name}, to‘lov qabul qilindi!\nXizmatingiz faollashtirildi 🎉"
    )

# ===== CHEK QABUL =====
@bot.message_handler(content_types=['photo'])
def get_check(m):
    if not orders:
        return
    order_id = list(orders.keys())[-1]

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{order_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"no_{order_id}")
    )

    bot.send_photo(
        ADMIN_CHAT_ID,
        m.photo[-1].file_id,
        caption=f"💳 Karta to‘lovi\n🆔 Buyurtma: {order_id}\n👤 User: {m.chat.id}",
        reply_markup=kb
    )

    bot.send_message(m.chat.id, "⏳ Chek adminga yuborildi.")

# ===== ADMIN PANEL =====
@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok_", "no_")))
def admin_panel(c):
    action, order_id = c.data.split("_")
    order_id = int(order_id)
    user_id = orders[order_id]["user"]

    if action == "ok":
        bot.send_message(user_id, "✅ To‘lov tasdiqlandi! 🎉")
    else:
        bot.send_message(user_id, "❌ To‘lov rad etildi.")

    orders.pop(order_id, None)
    bot.answer_callback_query(c.id)

# ===== ORQAGA =====
@bot.message_handler(func=lambda m: m.text == "⬅️ Orqaga")
def back(m):
    user_state.pop(m.chat.id, None)
    start(m)

# ===== RUN =====
print("✅ PRO bot ishga tushdi")
bot.infinity_polling(skip_pending=True)
