import telebot
from telebot import types
from telebot.types import LabeledPrice

TOKEN = "6673316226:AAFqXnQqvz6pXegT8VLMQ3axck0SFN40RZ4"
ADMIN_ID = 5272623103

bot = telebot.TeleBot(TOKEN)

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
        f"🎉 Xush kelibsiz, {name}!\n\nXizmatlardan birini tanlang 👇",
        reply_markup=kb
    )

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

# ================= TUG‘ILGAN KUN =================
@bot.message_handler(func=lambda m: m.text == "⏳ Tug‘ilgan kun qachon?")
def birthday(m):
    kb = types.InlineKeyboardMarkup(row_width=3)
    for i in range(1, 7):
        kb.add(types.InlineKeyboardButton(str(i), callback_data=f"bd_{i}"))

    bot.send_photo(
        m.chat.id,
        open("images/preview/birthday.png", "rb"),
        caption="1–2 bepul, 3–6 pullik",
        reply_markup=kb
    )

# ================= SHABLON =================
@bot.message_handler(func=lambda m: m.text == "🖼 Rasmli tabriklar")
def shablon(m):
    kb = types.InlineKeyboardMarkup(row_width=4)
    for i in range(1, 13):
        kb.add(types.InlineKeyboardButton(str(i), callback_data=f"sh_{i}"))

    bot.send_photo(
        m.chat.id,
        open("images/preview/shablon.png", "rb"),
        caption="1–2 bepul, qolganlari pullik",
        reply_markup=kb
    )

# ================= RASM TANLASH =================
@bot.callback_query_handler(func=lambda c: c.data.startswith(("bd_", "sh_")))
def choose_image(c):
    chat_id = c.message.chat.id
    kind, num = c.data.split("_")
    num = int(num)

    path = (
        f"images/birthday/birthday{num}.png"
        if kind == "bd"
        else f"images/shablon/{num}.png"
    )

    if num <= 2:
        bot.send_photo(chat_id, open(path, "rb"))
        return

    user_orders[chat_id] = {"path": path, "num": num}

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⭐ Telegram Stars — 10", callback_data="pay_stars"))
    kb.add(types.InlineKeyboardButton("💳 Karta — 2 000 so‘m", callback_data="pay_card"))

    bot.send_message(
        chat_id,
        f"🔒 <b>🖼 #{num} Rasm pullik</b>\n\n"
        "Rasmni olish uchun avval to‘lovni amalga oshiring.",
        parse_mode="HTML",
        reply_markup=kb
    )

# ================= STARS =================
@bot.callback_query_handler(func=lambda c: c.data == "pay_stars")
def stars(c):
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

@bot.message_handler(content_types=['successful_payment'])
def stars_success(m):
    order = user_orders.pop(m.chat.id, None)
    if order:
        bot.send_photo(m.chat.id, open(order["path"], "rb"))
    bot.send_message(m.chat.id, "✅ Stars to‘lovi qabul qilindi!")

# ================= KARTA =================
@bot.callback_query_handler(func=lambda c: c.data == "pay_card")
def card(c):
    chat_id = c.message.chat.id
    waiting_check.add(chat_id)

    order = user_orders.get(chat_id)
    if not order:
        bot.send_message(chat_id, "❌ Tanlangan rasm topilmadi.")
        return

    num = order["num"]

    bot.send_message(
        chat_id,
        f"🖼 #{num} Rasm muvaffaqiyatli tanlandi!\n\n"
        "💳 <b>Karta orqali to‘lov:</b>\n\n"
        "🖼 Rasm narxi: <b>2 000 so‘m</b>\n\n"
        "💳 <code>4073420087931386</code>\n"
        "👤 Abrorjon Urayimov\n\n"
        "📸 Iltimos, to‘lovdan keyin chek rasmini yuboring.\n\n"
        "✅ To‘lovdan so‘ng tanlangan rasm admin tasdiqlashi bilan sizga yuboriladi.",
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
