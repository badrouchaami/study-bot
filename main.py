import os
import telebot
from groq import Groq

# جلب المفاتيح من متغيرات البيئة السحابية لأمان أشد
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أنا بوت الدراسة الذكي. أرسل لي أي سؤال أو تمرين وسأقوم بحله لك فوراً!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # إرسال السؤال إلى عقل الذكاء الاصطناعي Groq
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "أنت مساعد دراسي خبير ومبسط للعلوم والمعارف. أجب عن أسئلة الطالب بدقة وشرح موضح خطوة بخطوة باللغة العربية."
                },
                {
                    "role": "user",
                    "content": message.text,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        response = chat_completion.choices[0].message.content
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء معالجة طلبك، يرجى المحاولة لاحقاً.")

if __name__ == "__main__":
    bot.infinity_polling()
