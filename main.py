import os
import telebot
from flask import Flask, request
from groq import Groq

# قراءة المتغيرات السرية من إعدادات Render
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running live!", 200


# نقطة استقبال الرسائل من تيليجرام (Webhook)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  json_string = request.get_data().decode("utf-8")
  update = telebot.types.Update.de_json(json_string)
  bot.process_new_updates([update])
  return "!", 200


# الرد على رسائل المستخدمين النصية
@bot.message_handler(func=lambda message: True)
def handle_message(message):
  try:
    chat_id = message.chat.id
    user_text = message.text

    # إرسال رسالة انتظار مؤقتة
    sent_msg = bot.send_message(chat_id, "جاري التفكير وصياغة الإجابة... 🤖")

    # الاتصال بنموذج Groq
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role":
                "system",
            "content":
                "أنت بوت دراسي ذكي ومساعد تعليمي ممتاز، ساعد الطالب بكل دقة واحترافية.",
        }, {
            "role": "user",
            "content": user_text,
        }],
    )

    answer = completion.choices[0].message.content
    bot.edit_message_text(answer, chat_id=chat_id, message_id=sent_msg.message_id)

  except Exception as e:
    bot.send_message(
        message.chat.id,
        "عذراً، حدث خطأ في معالجة طلبك. تأكد من صحة مفتاح Groq API في إعدادات"
        " Render.",
    )


if __name__ == "__main__":
  # ضبط الـ Webhook تلقائياً مع خوادم تيليجرام
  RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
  if RENDER_URL:
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")

  # تشغيل خادم Flask
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)
      
