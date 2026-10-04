import telebot
from telebot import types
import sqlite3

TOKEN = "8945005229:AAGuGnAi9UDHj0yNb7PU8_V4-wbAsBKwUZ4"
ADMIN_ID = 8863100986
KASPI_CARD = "4400430372724556"
KASPI_NAME = "Ақбөбек.Қ"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
conn = sqlite3.connect("shop.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item TEXT, price INTEGER, nick TEXT, status TEXT, msg_id INTEGER)")
conn.commit()

last_msg = {}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("💎 Robux", callback_data="robux_rules"),
           types.InlineKeyboardButton("🔪 MM2", callback_data="mm2_cat"))
    # ОТПРАВЛЯЕМ БАННЕР
    with open("banner.jpg", "rb") as photo:
        msg = bot.send_photo(m.chat.id, photo, caption="👑 <b>ROBUX & MM2 SHOP KZ</b>\nДешево и безопасно!", reply_markup=kb, parse_mode="HTML")
    last_msg[m.chat.id] = msg.message_id

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    chat_id = c.message.chat.id
    msg_id = c.message.message_id
    last_msg[chat_id] = msg_id

    if c.data == "robux_rules":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ Подтвердить и купить", callback_data="robux_ok"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
        bot.edit_message_caption(
            "📜 <b>Правила и условия покупки Robux</b>\n\n"
            "<b>1. Требования:</b> Акк старше 1 года + плейс.\n"
            "<b>2. Комиссию берем на себя!</b>\n"
            "<b>3. Сроки: Pending 5-7 дней.</b>\n"
            "<b>4. Без паролей!</b>",
            chat_id, msg_id, reply_markup=kb, parse_mode="HTML")

    elif c.data == "mm2_cat":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔮 Godly", callback_data="mm2_godly_rules"),
               types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
        bot.edit_message_caption("🔪 <b>Выбери категорию MM2:</b>", chat_id, msg_id, reply_markup=kb, parse_mode="HTML")

    elif c.data == "mm2_godly_rules":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ Подтвердить и купить", callback_data="mm2_godly_ok"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="mm2_cat"))
        bot.edit_message_caption(
            "🔪 <b>Правила Godly MM2</b>\n"
            "1. Акк старше 1 года, трейды вкл.\n"
            "2. Передача через трейд/VIP.\n"
            "3. Моментально, без комиссии.",
            chat_id, msg_id, reply_markup=kb, parse_mode="HTML")

    elif c.data == "robux_ok":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton("100 R$ - 600 тг", callback_data="buy_robux_100_600"),
               types.InlineKeyboardButton("500 R$ - 3000 тг", callback_data="buy_robux_500_3000"))
        kb.add(types.InlineKeyboardButton("✏️ Любое кол-во", callback_data="robux_custom"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="robux_rules"))
        bot.edit_message_caption("💎 <b>Выбери пак:</b>", chat_id, msg_id, reply_markup=kb, parse_mode="HTML")

    elif c.data == "robux_custom":
        cur.execute("INSERT INTO orders (user_id, status, msg_id) VALUES (?,?,?)", (c.from_user.id, "wait_custom_amount", msg_id))
        conn.commit()
        bot.edit_message_caption("✏️ <b>Напиши любое кол-во Robux</b>\nНапример: 777", chat_id, msg_id, reply_markup=None, parse_mode="HTML")

    elif c.data == "mm2_godly_ok":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Gemstone - 800 тг", callback_data="buy_mm2_Gemstone_800"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="mm2_godly_rules"))
        bot.edit_message_caption("🔮 <b>Godly в наличии:</b>", chat_id, msg_id, reply_markup=kb, parse_mode="HTML")

    elif c.data == "back":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton("💎 Robux", callback_data="robux_rules"),
               types.InlineKeyboardButton("🔪 MM2", callback_data="mm2_cat"))
        bot.edit_message_caption("👑 <b>ROBUX & MM2 SHOP KZ</b>", chat_id, msg_id, reply_markup=kb, parse_mode="HTML")

    elif c.data.startswith("buy_"):
        price = int(c.data.split("_")[-1])
        item = c.data.replace("buy_","").rsplit("_",1)[0].replace("_"," ").upper()
        cur.execute("INSERT INTO orders (user_id, item, price, status, msg_id) VALUES (?,?,?,?,?)", (c.from_user.id, item, price, "wait", msg_id))
        conn.commit()
        oid = cur.lastrowid
        cur.execute("UPDATE orders SET status=? WHERE id=?", (f"wait_nick_{oid}", oid))
        conn.commit()
        bot.edit_message_caption(f"🧾 Заказ #{oid}: {item}\n\n✏️ Напиши ник:", chat_id, msg_id, parse_mode="HTML")

    elif c.data.startswith("check_"):
        oid = c.data.split("_")[1]
        cur.execute("UPDATE orders SET status='checking' WHERE id=?", (oid,))
        conn.commit()
        bot.edit_message_caption(f"📎 Отправь фото чека для #{oid}", chat_id, msg_id, parse_mode="HTML")

@bot.message_handler(content_types=['text'])
def text_handler(m):
    try: bot.delete_message(m.chat.id, m.message_id)
    except: pass
    cur.execute("SELECT id, msg_id FROM orders WHERE user_id=? AND status='wait_custom_amount' ORDER BY id DESC LIMIT 1", (m.from_user.id,))
    custom = cur.fetchone()
    if custom:
        oid_tmp, msg_id = custom
        msg_id = msg_id or last_msg.get(m.chat.id)
        if not m.text.isdigit():
            bot.edit_message_caption("❌ Только цифрами! Напр: 350", m.chat.id, msg_id, parse_mode="HTML")
            return
        amount = int(m.text)
        price = amount * 6
        cur.execute("UPDATE orders SET item=?, price=?, status=? WHERE id=?", (f"{amount} R$ ROBUX", price, f"wait_nick_{oid_tmp}", oid_tmp))
        conn.commit()
        bot.edit_message_caption(f"🧾 {amount} R$ = {price} тг\n\n✏️ Напиши ник:", m.chat.id, msg_id, parse_mode="HTML")
        return
    cur.execute("SELECT id, item, price, msg_id FROM orders WHERE user_id=? AND status LIKE 'wait_nick_%' ORDER BY id DESC LIMIT 1", (m.from_user.id,))
    r = cur.fetchone()
    if r:
        oid, item, price, msg_id = r
        msg_id = msg_id or last_msg.get(m.chat.id)
        cur.execute("UPDATE orders SET nick=?, status='wait_pay' WHERE id=?", (m.text, oid))
        conn.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📎 Я оплатил", callback_data=f"check_{oid}"))
        bot.edit_message_caption(f"💳 <code>{KASPI_CARD}</code>\nЗаказ #{oid}\nНик: {m.text}\n{item} - {price} тг", m.chat.id, msg_id, reply_markup=kb, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def photo_handler(m):
    try: bot.delete_message(m.chat.id, m.message_id)
    except: pass
    cur.execute("SELECT id, msg_id FROM orders WHERE user_id=? AND status='checking' ORDER BY id DESC LIMIT 1", (m.from_user.id,))
    r = cur.fetchone()
    if not r: return
    oid, msg_id = r
    msg_id = msg_id or last_msg.get(m.chat.id)
    cur.execute("UPDATE orders SET status='paid' WHERE id=?", (oid,))
    conn.commit()
    bot.edit_message_caption(f"✅ Чек #{oid} принят! Жди.", m.chat.id, msg_id, parse_mode="HTML")
    bot.send_message(ADMIN_ID, f"Заказ #{oid}")
    bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)

bot.infinity_polling()