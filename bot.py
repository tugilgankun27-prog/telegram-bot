import telebot
from telebot import types
from telebot.types import LabeledPrice
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5272623103

bot = telebot.TeleBot(BOT_TOKEN)

# ================= MA'LUMOTLAR =================
user_state = {}      # chat_id: "shablon" | "birthday"
user_orders = {}     # chat_id: {"path": ..., "num": ...}
waiting_check = set()

# ================= START =================
@bot.message_handler(commands=["start"])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🖼 Rasmli tabriklar")
    kb.add("⏳ Tug‘ilgan kun qachon?")
    kb.add("📞 Kutilmagan qo‘ng‘iroq loyihasi")

    name = m.from_user.first_name or "Do‘stimiz"
    bot.send_message(
        m.chat.id,
        f"🎉 Xush kelibsiz, {name}!\n\nXizmatni tanlang 👇",
        reply_markup=kb
    )

# ================= KUTILMAGAN QO‘NG‘IROQ =================
@bot.message_handler(func=lambda m: m.text == "📞 Kutilmagan qo‘ng‘iroq loyihasi")
def call_project(m):
    bot.send_message(
        m.chat.id,
        "📞 <b>Kutilmagan qo‘ng‘iroq loyihasi</b>\n\n"
        "💰 Narx: <b>65 000 so‘m</b>\n"
        "📩 Admin: @Tugilgan_kun_admin",
        parse_mode="HTML"
    )

# ================= SHABLON =================
@bot.message_handler(func=lambda m: m.text == "🖼 Rasmli tabriklar")
def shablon(m):
    user_state[m.chat.id] = "shablon"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("1", "2", "3", "4")
    kb.row("5", "6", "7", "8")
    kb.row("9", "10", "11", "12")
    kb.add("⬅️ Orqaga")

    bot.send_photo(
        m.chat.id,
        open("images/preview/shablon.png", "rb"),
        caption="🟢 1–2-rasmlar bepul\n🔒 Qolgan rasmlar pullik",
        reply_markup=kb
    )

# ================= BIRTHDAY =================
@bot.message_handler(func=lambda m: m.text == "⏳ Tug‘ilgan kun qachon?")
def birthday(m):
    user_state[m.chat.id] = "birthday"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("1", "2", "3")
    kb.row("4", "5", "6")
    kb.add("⬅️ Orqaga")

    bot.send_photo(
        m.chat.id,
        open("images/preview/birthday.png", "rb"),
        caption="🟢 1–2 bepul\n🔒 3–6 pullik",
        reply_markup=kb
    )

# ================= RAQAM TANLASH =================
@bot.message_handler(func=lambda m: m.text.isdigit())
def choose_image(m):
    chat_id = m.chat.id
    num = int(m.text)
    state = user_state.get(chat_id)

    if not state:
        return

    path = (
        f"images/shablon/{num}.png"
        if state == "shablon"
        else f"images/birthday/birthday{num}.png"
    )

    if not os.path.exists(path):
        bot.send_message(chat_id, "❌ Rasm topilmadi")
        return

    # ===== BEPUL =====
    if num <= 2:
        bot.send_photo(chat_id, open(path, "rb"), caption="✅ Bepul rasm")
        return

    # ===== PULLIK =====
    user_orders[chat_id] = {"path": path, "num": num}

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⭐ Telegram Stars — 10", callback_data="pay_stars"))
    kb.add(types.InlineKeyboardButton("💳 Karta — 2 000 so‘m", callback_data="pay_card"))

    bot.send_message(
        chat_id,
        f"🔒 <b>#{num} tanlagan rasmingiz pullik</b>\n\n"
        "Tanlagan rasmingizni olish uchun <b>to‘lovni amalga oshirishingiz kerak</b>.",
        parse_mode="HTML",
        reply_markup=kb
    )

# ================= STARS =================
@bot.callback_query_handler(func=lambda c: c.data == "pay_stars")
def pay_stars(c):
    prices = [LabeledPrice("Premium rasm", 10)]
    bot.send_invoice(
        chat_id=c.message.chat.id,
        title="Premium rasm",
        description="Telegram Stars orqali to‘lov",
        provider_token="",
        currency="XTR",
        prices=prices,
        invoice_payload="stars_10"
    )

@bot.message_handler(content_types=["successful_payment"])
def stars_success(m):
    order = user_orders.pop(m.chat.id, None)
    if order:
        bot.send_photo(m.chat.id, open(order["path"], "rb"))
        bot.send_message(m.chat.id, "✅ To‘lov qabul qilindi!")

# ================= KARTA =================
@bot.callback_query_handler(func=lambda c: c.data == "pay_card")
def pay_card(c):
    chat_id = c.message.chat.id
    waiting_check.add(chat_id)

    order = user_orders.get(chat_id)
    if not order:
        return

    num = order["num"]

    bot.send_message(
        chat_id,
        f"🖼 <b>#{num} tanlangan rasm</b>\n\n"
        "💳 <b>Karta orqali to‘lov:</b>\n\n"
        "🖼 Rasm narxi: <b>2 000 so‘m</b>\n\n"
        "💳 <code>4073420087931386</code>\n"
        "👤 Abrorjon Urayimov\n\n"
        "📸 To‘lovdan keyin chek rasmini yuboring.\n\n"
        "✅ Admin tasdiqlagach rasm yuboriladi.",
        parse_mode="HTML"
    )

# ================= CHEK =================
@bot.message_handler(content_types=["photo"])
def check(m):
    if m.chat.id not in waiting_check:
        return

    user = m.from_user
    uid = user.id

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{uid}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"no_{uid}")
    )

    bot.send_photo(
        ADMIN_ID,
        m.photo[-1].file_id,
        caption=f"💳 <b>To‘lov cheki</b>\n\n👤 {user.first_name}\n🆔 <code>{uid}</code>",
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

# ================= ORQAGA =================
@bot.message_handler(func=lambda m: m.text == "⬅️ Orqaga")
def back(m):
    state = user_state.get(m.chat.id)
    if state == "shablon":
        shablon(m)
    elif state == "birthday":
        birthday(m)

# ================= RUN =================
print("Bot ishga tushdi")
bot.infinity_polling(skip_pending=True)
