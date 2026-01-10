import telebot
from telebot import types
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# ================= START / BOSH MENYU =================
def main_menu(chat_id, name="Do‘stimiz"):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🖼 Rasmli tabriklar")
    kb.add("⏳ Tug‘ilgan kun qachon?")
    kb.add("📞 Kutilmagan qo‘ng‘iroq")

    bot.send_message(
        chat_id,
        f"🎉 Xush kelibsiz, {name}!\n\nXizmatlardan birini tanlang 👇",
        reply_markup=kb
    )

@bot.message_handler(commands=["start"])
def start(m):
    name = m.from_user.first_name or "Do‘stimiz"
    main_menu(m.chat.id, name)

# ================= RASMLI TABRIKLAR =================
@bot.message_handler(func=lambda m: m.text == "🖼 Rasmli tabriklar")
def rasmli_tabriklar(m):
    # pastki tugmalar (raqamlar + orqaga)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("1", "2", "3", "4")
    kb.row("5", "6", "7", "8")
    kb.add("♻️ Orqaga")

    # rasm ustidagi inline emas, faqat rasm
    bot.send_photo(
        m.chat.id,
        open("images/preview/shablon.png", "rb"),
        caption="🟢 Kerakli raqamni tanlang!"
    )

    bot.send_message(
        m.chat.id,
        "⬇️ Raqamni tanlang:",
        reply_markup=kb
    )

# ================= TUG‘ILGAN KUN =================
@bot.message_handler(func=lambda m: m.text == "⏳ Tug‘ilgan kun qachon?")
def tugilgan_kun(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("1", "2", "3")
    kb.row("4", "5", "6")
    kb.add("♻️ Orqaga")

    bot.send_photo(
        m.chat.id,
        open("images/preview/birthday.png", "rb"),
        caption="🟢 Kerakli raqamni tanlang!"
    )

    bot.send_message(
        m.chat.id,
        "⬇️ Raqamni tanlang:",
        reply_markup=kb
    )

# ================= ORQAGA (BIR BOSQICH ORTGA) =================
@bot.message_handler(func=lambda m: m.text == "♻️ Orqaga")
def back(m):
    # bosh menyuga qaytmaydi, faqat oldingi umumiy menyu
    main_menu(m.chat.id, m.from_user.first_name)

# ================= KUTILMAGAN QO‘NG‘IROQ =================
@bot.message_handler(func=lambda m: m.text == "📞 Kutilmagan qo‘ng‘iroq")
def call_project(m):
    text = (
        "📞 <b>Kutilmagan qo‘ng‘iroq loyihasi</b>\n\n"
        "Yaqinlaringizni professional tabrik bilan xursand qiling 🎉\n\n"
        "💰 Narx: <b>65 000 so‘m</b>\n"
        "📩 Admin: @Tugilgan_kun_admin"
    )
    bot.send_message(m.chat.id, text, parse_mode="HTML")

# ================= RASMLARNI TANLASH (1–12 / 1–6) =================
@bot.message_handler(func=lambda m: m.text.isdigit())
def choose_image(m):
    num = int(m.text)

    if 1 <= num <= 12:
        path1 = f"images/shablon/{num}.png"
        path2 = f"images/birthday/birthday{num}.png"

        if os.path.exists(path1):
            bot.send_photo(m.chat.id, open(path1, "rb"))
        elif os.path.exists(path2):
            bot.send_photo(m.chat.id, open(path2, "rb"))
        else:
            bot.send_message(m.chat.id, "❌ Bu raqamga rasm topilmadi.")

# ================= RUN =================
print("Bot ishga tushdi")
bot.infinity_polling(skip_pending=True)
