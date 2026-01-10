import telebot
from telebot import types
from telebot.types import LabeledPrice
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5272623103

bot = telebot.TeleBot(BOT_TOKEN)

# ===== MA'LUMOTLAR =====
user_orders = {}      # {chat_id: {"path": ..., "num": ...}}
waiting_check = set()

# ================= START =================
@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⏳ Tug‘ilgan kun qachon?")
    kb.add("🖼 Rasmli tabriklar")
    kb.add("📞 Kutilmagan qo‘ng‘iroq loyihasi")

    name = m.from_user.first_name or "Do‘stimiz"
    bot.send_message(
        m.chat.id,
        f"🏠 Bosh sahifa\n\n🎉 Xush kelibsiz, {name}!\nXizmatlardan birini tanlang 👇",
        reply_markup=kb
    )

# ================= ORQAGA =================
@bot.message_handler(func=lambda m: m.text == "♻️ Orqaga")
def back(m):
    start(m)

# ================= KUTILMAGAN QO‘NG‘IROQ =================
@bot.message_handler(func=lambda m: m.text == "📞 Kutilmagan qo‘ng‘iroq loyihasi")
def call_project(m):
    text = (
        "📞 <b>Kutilmagan Qo‘ng‘iroq Loyihasi</b>\n\n"
        "Kutilmagan Qo‘ng‘iroq Loyihasi orqali yaqinlaringizni xursand qiling!\n"
        "Eng chiroyli tabriklar faqat bizda! 🎉\n\n"
        "💰 <b>Xizmat pullik:</b> 65 000 so‘m\n\n"
        "📌 Namuna: @tabrik_tugulgan_kun\n"
        "📩 Murojaat: @Tugilgan_kun_admin"
    )
    bot.send_message(m.chat.id, text, parse_mode="HTML")

# ================= TUG‘ILGAN KUN (PREVIEW + RAQAMLAR) =================
@bot.message_handler(func=lambda m: m.text == "⏳ Tug‘ilgan kun qachon?")
def birthday(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("1", "2", "3")
    kb.row("4", "5", "6")
    kb.row("♻️ Orqaga")

    bot.send_photo(
        m.chat.id,
        open("images/preview/birthday.png", "rb"),
        caption="🟢 Kerakli raqamni tanlang.\n\n1–2 bepul, 3–6 pullik",
        reply_markup=kb
    )

# ================= RASM TANLASH (REPLY) =================
@bot.message_handler(func=lambda m: m.text.isdigit() and 1 <= int(m.text) <= 6)
def choose_birthday_image(m):
    chat_id = m.chat.id
    num = int(m.text)
    path = f"images/birthday/birthday{num}.png"

    if num <= 2:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("♻️ Orqaga")
        bot.send_photo(
            chat_id,
            open(path, "rb"),
            caption="✅ Bepul rasm",
            reply_markup=kb
        )
        return

    user_orders[chat_id] = {"path": path, "num": num}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⭐ Telegram Stars")
    kb.add("💳 Karta orqali to‘lov")
    kb.add("♻️ Orqaga")

    bot.send_message(
        chat_id,
        f"🔒 #{num} rasm pullik.\nTo‘lov turini tanlang:",
        reply_markup=kb
    )

# ================= STARS =================
@bot.message_handler(func=lambda m: m.text == "⭐ Telegram Stars")
def stars(m):
    prices = [LabeledPrice("Premium rasm", 10)]
    bot.send_invoice(
        chat_id=m.chat.id,
        title="Premium rasm",
        description="Telegram Stars orqali to‘lov",
        provider_token="",
        currency="XTR",
        prices=prices,
        invoice_payload="stars_10"
    )

@bot.message_handler(content_types=['successful_payment'])
def stars_success(m):
    order = user_orders.pop(m.chat.id, None)
    if order:
        bot.send_photo(m.chat.id, open(order["path"], "rb"))
    bot.send_message(m.chat.id, "✅ Stars to‘lovi qabul qilindi!")

# ================= KARTA =================
@bot.message_handler(func=lambda m: m.text == "💳 Karta orqali to‘lov")
def card(m):
    chat_id = m.chat.id
    waiting_check.add(chat_id)

    order = user_orders.get(chat_id)
    if not order:
        bot.send_message(chat_id, "❌ Tanlangan rasm topilmadi.")
        return

    num = order["num"]

    bot.send_message(
        chat_id,
        f"🖼 #{num} rasm tanlandi.\n\n"
        "💳 <b>Karta orqali to‘lov:</b>\n"
        "<b>2 000 so‘m</b>\n\n"
        "💳 <code>4073420087931386</code>\n"
        "👤 Abrorjon Urayimov\n\n"
        "📸 To‘lovdan keyin chek rasmini yuboring.",
        parse_mode="HTML"
    )

# ================= CHEK =================
@bot.message_handler(content_types=['photo'])
def check(m):
    if m.chat.id not in waiting_check:
        return

    user = m.from_user
    uid = user.id

    caption = (
        "💳 <b>To‘lov cheki</b>\n\n"
        f"👤 {user.first_name}\n"
        f"🆔 <code>{uid}</code>"
    )

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{uid}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"no_{uid}")
    )

    bot.send_photo(
        ADMIN_ID,
        m.photo[-1].file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=kb
    )

    bot.send_message(m.chat.id, "⏳ Chek admin tekshiruviga yuborildi.")

# ================= ADMIN =================
@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok_", "no_")))
def admin_decision(c):
    action, uid = c.data.split("_")
    uid = int(uid)

    if action == "ok":
        order = user_orders.pop(uid, None)
        if order:
            bot.send_photo(uid, open(order["path"], "rb"))
        bot.send_message(uid, "✅ To‘lov tasdiqlandi!")
    else:
        bot.send_message(uid, "❌ To‘lov rad etildi")

    waiting_check.discard(uid)
    bot.edit_message_caption("✅ Yakunlandi", ADMIN_ID, c.message.message_id)

# ================= RUN =================
print("Bot ishga tushdi")
bot.infinity_polling(skip_pending=True)
