import telebot
from confiig import TOKEN
import sqlite3
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, amount INTEGER, date TEXT)")
conn.commit()
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я Вадик готов тебе помочь")
@bot.message_handler(commands=['total'])
def total(message):
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (message.from_user.id,))
    result = cursor.fetchone()[0]
    if result is None:
        result =0
    bot.send_message(message.chat.id, "Всего потрачено: " + str(result) + "тенге")
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Что я умею: \n/start - приветствие\n/total - суммирует\n/reset - сбросить траты\n/help - спиок команд\n\nЧтобы записать траты, напиши: вода 350")
@bot.message_handler(commands=['reset'])
def reset(message):
    cursor.execute("DELETE FROM expenses WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    bot.send_message(message.chat.id, "Готово, траты сброшены. Можно начинать заново")
@bot.message_handler(func=lambda message: True)
def add_expense(message):
    lines = message.text.split("\n")
    saved = []
    for line in lines:
        parts = line.split()
        if len(parts) < 2 or not parts[-1].isdigit():
            continue
        name = " ".join(parts[:-1])
        amount = int(parts[-1])
        cursor.execute("INSERT INTO expenses (user_id, name, amount, date) VALUES (?, ?, ?, date('now'))", (message.from_user.id, name, amount))
        conn.commit()
        saved.append(name + ", " + str(amount) + "тенге")
    if not saved:
        bot.send_message(message.chat.id, "Напиши чего нибудь: ")
        return
    bot.send_message(message.chat.id, "Записал: \n" + "\n".join(saved))
bot.set_my_commands([
    telebot.types.BotCommand("start", "Приветствие"),
    telebot.types.BotCommand("total", "суммирует"),
    telebot.types.BotCommand("reset", "сбросить траты"),
    telebot.types.BotCommand("help", "список команд"),
])
bot.polling()