# -*- coding: utf-8 -*-
"""
Бот-видача промптів для команди онлайн-школи.

Як це працює:
- Людина пише /start -> бачить меню відділів (кнопки).
- Обирає відділ -> бачить список промптів цього відділу (кнопки).
- Обирає промпт -> бот надсилає Біль, Завдання, готовий текст промпту
  (одним повідомленням, з кодовим блоком — Telegram сам покаже кнопку
  "скопіювати" на довгому тексті) і коротку інструкцію "як користуватись".
- Якщо людина просто пише текст (не кнопкою) — бот шукає збіги
  за заголовками і Болем усіх промптів і пропонує схожі варіанти.

Залежності: лише модуль `requests` (стандартний, є майже всюди).
Не використовує aiogram/python-telegram-bot спеціально — менше шансів
зловити несумісність версій бібліотеки при розгортанні.

ЗАПУСК:
  1. pip install requests
  2. Встановіть змінну середовища BOT_TOKEN (див. інструкцію в README.md)
  3. python bot.py

Бот працює через long polling — це означає, що процес має бути
постійно запущений (див. README.md про безкоштовний хостинг Railway/Render).
"""

import os
import time
import logging
from typing import Optional

import requests
import google.generativeai as genai

from data import DEPARTMENTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("prompts-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit(
        "Не задано BOT_TOKEN. Встановіть змінну середовища BOT_TOKEN "
        "(токен отримаєте у @BotFather в Telegram) і запустіть знову."
    )
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
MAX_TG_MESSAGE = 4096  # ліміт Telegram на довжину одного повідомлення


def api(method: str, **params):
    """Простий виклик методу Telegram Bot API."""
    try:
        resp = requests.post(f"{API_URL}/{method}", json=params, timeout=30)
        data = resp.json()
        if not data.get("ok"):
            log.warning("API error on %s: %s", method, data)
        return data
    except requests.RequestException as e:
        log.warning("Network error on %s: %s", method, e)
        return {"ok": False}


def send_message(chat_id: int, text: str, reply_markup: Optional[dict] = None, parse_mode: str = "HTML"):
    """Надсилання повідомлення з автоматичним поділом, якщо текст довший за ліміт Telegram."""
    if len(text) <= MAX_TG_MESSAGE:
        return api("sendMessage", chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    # Ріжемо по абзацах, щоб не розірвати текст промпту посередині слова
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > MAX_TG_MESSAGE - 100:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    result = None
    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        result = api(
            "sendMessage",
            chat_id=chat_id,
            text=chunk,
            reply_markup=reply_markup if is_last else None,
            parse_mode=parse_mode,
        )
    return result


def answer_callback(callback_query_id: str, text: str = ""):
    api("answerCallbackQuery", callback_query_id=callback_query_id, text=text)


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- Клавіатури ----------

def departments_keyboard() -> dict:
    rows = []
    for dept_id, dept in DEPARTMENTS.items():
        rows.append([{"text": dept["label"], "callback_data": f"dept:{dept_id}"}])
    return {"inline_keyboard": rows}


def prompts_keyboard(dept_id: str) -> dict:
    dept = DEPARTMENTS[dept_id]
    rows = []
    for p in dept["prompts"]:
        rows.append([{"text": p["title"], "callback_data": f"prompt:{dept_id}:{p['id']}"}])
    rows.append([{"text": "⬅️ Назад до відділів", "callback_data": "back:depts"}])
    return {"inline_keyboard": rows}


def back_keyboard(dept_id: str) -> dict:
    return {"inline_keyboard": [[{"text": "⬅️ Назад до списку", "callback_data": f"dept:{dept_id}"}]]}


# ---------- Пошук ----------

def find_prompt(dept_id: str, prompt_id: str):
    dept = DEPARTMENTS.get(dept_id)
    if not dept:
        return None
    for p in dept["prompts"]:
        if p["id"] == prompt_id:
            return p
    return None


STOP_WORDS = {
    "і", "й", "в", "у", "не", "на", "з", "із", "по", "для", "як", "що", "це",
    "до", "але", "а", "я", "ми", "ви", "він", "вона", "вони", "мені", "мій", "моя",
    "хочу", "потрібно", "треба", "щоб", "якщо", "або", "теж", "вже", "дуже",
}


def _keywords(text: str):
    words = [w.strip(".,!?()«»\"'") for w in text.lower().split()]
    return [w for w in words if len(w) >= 3 and w not in STOP_WORDS]


def search_prompts(query: str, limit: int = 8):
    """Шукає за заголовком, Болем і Завданням у всіх відділах.

    Розбиває запит на окремі слова (а не шукає фразу цілком) і порівнює
    за початком слова (перші 5 літер) — це грубий, але робочий аналог
    стемінгу, щоб «заперечення» знаходило «заперечень» тощо.
    Повертає список (dept_id, prompt), відсортований за кількістю збігів.
    """
    q_words = _keywords(query)
    if not q_words:
        return []
    stems = [w[:5] if len(w) > 5 else w for w in q_words]
    scored = []
    for dept_id, dept in DEPARTMENTS.items():
        for p in dept["prompts"]:
            haystack = f"{p['title']} {p['pain']} {p['task']}".lower()
            score = sum(1 for s in stems if s in haystack)
            if score > 0:
                scored.append((score, dept_id, p))
    scored.sort(key=lambda x: -x[0])
    return [(dept_id, p) for _, dept_id, p in scored[:limit]]

def smart_search_with_gemini(query: str):
    """Просить Gemini підібрати номери найбільш підходящих промптів зі списку."""
    if not GEMINI_API_KEY:
        return None
    catalog = []
    for dept_id, dept in DEPARTMENTS.items():
        for p in dept["prompts"]:
            catalog.append(f"{dept_id}:{p['id']} — {p['title']}: {p['pain']}")
    catalog_text = "\n".join(catalog)
    prompt = (
        f"Ось список промптів (формат dept:id — назва: біль):\n{catalog_text}\n\n"
        f"Користувач написав: «{query}»\n"
        f"Обери 1-3 НАЙБІЛЬШ підходящих промпти. Відповідай лише у форматі dept:id, "
        f"через кому, без пояснень. Наприклад: sales:s1,support:sup3"
    )
    try:
        response = gemini_model.generate_content(prompt)
        ids = response.text.strip().split(",")
        results = []
        for item in ids:
            item = item.strip()
            if ":" in item:
                d_id, p_id = item.split(":", 1)
                p = find_prompt(d_id.strip(), p_id.strip())
                if p:
                    results.append((d_id.strip(), p))
        return results
    except Exception as e:
        log.warning("Gemini error: %s", e)
        return None


# ---------- Форматування відповіді з промптом ----------

def format_prompt_message(dept_id: str, p: dict) -> str:
    return (
        f"<b>{escape_html(p['title'])}</b>\n\n"
        f"💡 <b>Біль:</b> {escape_html(p['pain'])}\n\n"
        f"🎯 <b>Завдання:</b> {escape_html(p['task'])}\n\n"
        f"<b>Промпт (скопіюйте повністю):</b>\n"
        f"<pre>{escape_html(p['prompt'])}</pre>\n\n"
        f"🔧 <b>Як користуватись:</b> {escape_html(p['howto'])}"
    )


# ---------- Обробники ----------

def handle_start(chat_id: int):
    text = (
        "👋 Привіт! Це бот-бібліотека готових ШІ-промптів для команди.\n\n"
        "Оберіть відділ кнопкою нижче — або просто напишіть словами вашу проблему "
        "(наприклад «заперечення» або «негатив»), і я знайду потрібний промпт."
    )
    send_message(chat_id, text, reply_markup=departments_keyboard())


def handle_text(chat_id: int, text: str):
    if text.strip().startswith("/start"):
        handle_start(chat_id)
        return

    results = smart_search_with_gemini(text)
    if not results:
        results = search_prompts(text)

    if not results:
        send_message(
            chat_id,
            "Нічого не знайшов за цим словом 🤔 ...",
        )
        return

    rows = [
        [{"text": f"{DEPARTMENTS[d]['label']} — {p['title']}", "callback_data": f"prompt:{d}:{p['id']}"}]
        for d, p in results
    ]
    send_message(
        chat_id,
        f"Знайшов {len(results)} відповідних промптів:",
        reply_markup={"inline_keyboard": rows},
    )


def handle_callback(callback_query: dict):
    cq_id = callback_query["id"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    data = callback_query.get("data", "")

    if data == "back:depts":
        answer_callback(cq_id)
        api("editMessageReplyMarkup", chat_id=chat_id, message_id=message_id, reply_markup=departments_keyboard())
        return

    if data.startswith("dept:"):
        dept_id = data.split(":", 1)[1]
        dept = DEPARTMENTS.get(dept_id)
        answer_callback(cq_id)
        if not dept:
            return
        api(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text=f"{dept['label']} — оберіть промпт:",
            reply_markup=prompts_keyboard(dept_id),
        )
        return

    if data.startswith("prompt:"):
        _, dept_id, prompt_id = data.split(":", 2)
        p = find_prompt(dept_id, prompt_id)
        answer_callback(cq_id)
        if not p:
            send_message(chat_id, "Промпт не знайдено, спробуйте /start ще раз.")
            return
        send_message(chat_id, format_prompt_message(dept_id, p), reply_markup=back_keyboard(dept_id))
        return

    answer_callback(cq_id)


# ---------- Головний цикл (long polling) ----------

def run():
    log.info("Бот запущено, чекаю повідомлень...")
    offset = 0
    while True:
        try:
            resp = api("getUpdates", offset=offset, timeout=25)
        except Exception as e:
            log.warning("Polling error: %s", e)
            time.sleep(3)
            continue

        if not resp or not resp.get("ok"):
            time.sleep(3)
            continue

        for update in resp.get("result", []):
            offset = update["update_id"] + 1
            try:
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    handle_text(chat_id, update["message"]["text"])
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])
            except Exception as e:
                log.exception("Помилка обробки апдейту: %s", e)


if __name__ == "__main__":
    run()
