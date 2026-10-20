import os
import telebot
from groq import Groq
from flask import Flask
from threading import Thread

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# معرف حسابك (الآدمن)
ADMIN_ID = 8858369314

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# خادم ويب لإبقاء البوت متصلاً 24/7 على Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is active!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# أمر البداية
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا بوت الدراسة الذكي. يمكنك طرح أي سؤال دراسي، وإذا كنت المشرف فيمكنك رفع كتب ودروس بصيغة PDF ليدرسها البوت!")

# استلام الملفات والكتب (خاص بك أنت فقط كأدمن)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        doc_name = message.document.file_name
        bot.reply_to(message, f"📥 تم استلام الكتاب `{doc_name}` بنجاح! جاري معالجته وإضافته لقاعدة المعرفة...")
    else:
        bot.reply_to(message, "🚫 عذراً، رفع الكتب والدروس متاح فقط للمشرف على البوت.")

# استقبال إجابات الطلاب واستفساراتهم
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "أنت مساعد دراسي خبير ومبسط. أجب عن أسئلة الطالب بدقة وشرح موضح خطوة بخطوة باللغة العربية."},
                {"role": "user", "content": message.text}
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء معالجة الطلب، يرجى المحاولة لاحقاً.")

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
    
