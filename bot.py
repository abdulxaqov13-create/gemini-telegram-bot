from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from google import genai
import sqlite3

# ===== SOZLAMALAR =====
TELEGRAM_BOT_TOKEN = "8244925056:AAE4_XIUcn2HI9XYeiXxr_bLEu3b2uEdfwI"
GEMINI_API_KEY = "AIzaSyCb6C-MP54V2mrGj9hyH_Ku0SeGw0xnmWo"
MODEL = "models/gemini-flash-latest"
# =====================

# Gemini
gemini = genai.Client(api_key=GEMINI_API_KEY)

# DB
conn = sqlite3.connect("memory.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS chat (
    chat_id INTEGER,
    role TEXT,
    text TEXT
)
""")
conn.commit()

def save(chat_id, role, text):
    cur.execute(
        "INSERT INTO chat VALUES (?, ?, ?)",
        (chat_id, role, text)
    )
    conn.commit()

def load(chat_id, limit=10):
    cur.execute(
        "SELECT role, text FROM chat WHERE chat_id=? ORDER BY rowid DESC LIMIT ?",
        (chat_id, limit)
    )
    rows = cur.fetchall()[::-1]
    return "\n".join([f"{r}: {t}" for r, t in rows])

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_text = update.message.text

    save(chat_id, "user", user_text)
    history = load(chat_id)

    prompt = f"""
Bu suhbat tarixi:
{history}

Foydalanuvchiga mantiqli davom ettirib javob ber:
"""

    response = gemini.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    answer = response.text
    save(chat_id, "assistant", answer)

    await update.message.reply_text(answer)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("🤖 Bot ishga tushdi (xotira bilan)...")
    app.run_polling()

if __name__ == "__main__":
    main()
