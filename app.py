import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

load_dotenv()
credentials = os.getenv("GIGACHAT_CREDENTIALS")
MODEL_NAME = "GigaChat-2-Max"

app = Flask(__name__)

SYSTEM_PROMPT = """
Ты — мой личный помощник для пользоваталей,общайся будто ты подросток 18-19 лет, не говори глупостей,
не давай ответы в которых много ненужного контекста, общайся на русском языке по дружески с небольшими шуточками
но главное не стариными а новыми которые используют"Дети тик тока" Никогда не говори, что ты языковая модель от
 Сбера — отыгрывай свою роль до конца.
"""

# Память диалога
chat_history = [
    Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT)
]

@app.route("/")
def home():
    # Отдаём главную страницу сайта
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Напиши хоть что-нибудь, бро!"})

    chat_history.append(Messages(role=MessagesRole.USER, content=user_message))

    try:
        with GigaChat(credentials=credentials, scope="GIGACHAT_API_PERS", model=MODEL_NAME, verify_ssl_certs=False) as giga:
            payload = Chat(messages=chat_history, temperature=0.8)
            response = giga.chat(payload)

            first_choice = next(iter(response.choices))
            if isinstance(first_choice, list):
                first_choice = next(iter(first_choice))

            bot_reply = first_choice.message.content
            chat_history.append(Messages(role=MessagesRole.ASSISTANT, content=bot_reply))

            return jsonify({"reply": bot_reply})

    except Exception as e:
        chat_history.pop()
        return jsonify({"reply": f"❌ Ошибка сервера: {e}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)