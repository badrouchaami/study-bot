import os
import telebot
from groq import Groq
from flask import Flask
from threading import Thread

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

ADMIN_ID = 8858369314

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

app = Flask('')

@app.route('/')
def home():
    return "Bot is active!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا بوت الدراسة الذكي. يمكنك طرح أي سؤال وسأجيبك فوراً.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"📥 تم استلام الملف بنجاح!")
    else:
        bot.reply_to(message, "🚫 عذراً، رفع الملفات متاح للمشرف فقط.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⚠️ يرجى كتابة السؤال نصياً حالياً وسأقوم بحله لك!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text:
        return
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "أنت مساعد دراسي خبير ومبسط لطلاب الثانوية. أجب بدقة وشرح مفصل باللغة العربية."},
                {"role": "user", "content": message.text}
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content
        bot.reply_to(message, response)
    except Exception as e:
        print(f"Groq API Error: {e}")
        bot.reply_to(message, f"خطأ من الخادم: تأكد من صحة مفتاح Groq API في إعدادات Render.")

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
        
