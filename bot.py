# -*- coding: utf-8 -*-
"""
Бот-выдача промптов для команды онлайн-школы.

Как это работает:
- Человек пишет /start -> видит меню отделов (кнопки).
- Выбирает отдел -> видит список промптов этого отдела (кнопки).
- Выбирает промпт -> бот присылает Боль, Задачу, готовый текст промпта
  (одним сообщением, с кодовым блоком — Telegram сам покажет кнопку
  "скопировать" на длинном тексте) и короткую инструкцию "как пользоваться".
- Если человек просто пишет текст (не кнопкой) — бот ищет совпадения
  по заголовкам и Боли всех промптов и предлагает похожие варианты.

Зависимости: только модуль `requests` (стандартный, есть почти везде).
Не использует aiogram/python-telegram-bot специально — меньше шансов
поймать несовместимость версий библиотеки при разворачивании.

ЗАПУСК:
  1. pip install requests
  2. Установите переменную окружения BOT_TOKEN (см. инструкцию в README.md)
  3. python bot.py

Бот работает через long polling — это значит, что процесс должен быть
постоянно запущен (см. README.md про бесплатный хостинг Railway/Render).
"""

import os
import time
import logging
from typing import Optional

import requests

from data import DEPARTMENTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("prompts-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit(
        "Не задан BOT_TOKEN. Установите переменную окружения BOT_TOKEN "
        "(токен вы получите у @BotFather в Telegram) и запустите снова."
    )

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
MAX_TG_MESSAGE = 4096  # лимит Telegram на длину одного сообщения


def api(method: str, **params):
    """Простой вызов метода Telegram Bot API."""
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
    """Отправка сообщения с автоматической разбивкой, если текст длиннее лимита Telegram."""
    if len(text) <= MAX_TG_MESSAGE:
        return api("sendMessage", chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    # Режем по абзацам, чтобы не разорвать текст промпта посередине слова
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


# ---------- Клавиатуры ----------

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
    rows.append([{"text": "⬅️ Назад к отделам", "callback_data": "back:depts"}])
    return {"inline_keyboard": rows}


def back_keyboard(dept_id: str) -> dict:
    return {"inline_keyboard": [[{"text": "⬅️ Назад к списку", "callback_data": f"dept:{dept_id}"}]]}


# ---------- Поиск ----------

def find_prompt(dept_id: str, prompt_id: str):
    dept = DEPARTMENTS.get(dept_id)
    if not dept:
        return None
    for p in dept["prompts"]:
        if p["id"] == prompt_id:
            return p
    return None


def search_prompts(query: str, limit: int = 8):
    """Ищет по заголовку и Боли во всех отделах. Возвращает список (dept_id, prompt)."""
    q = query.lower().strip()
    if not q:
        return []
    results = []
    for dept_id, dept in DEPARTMENTS.items():
        for p in dept["prompts"]:
            haystack = f"{p['title']} {p['pain']}".lower()
            if q in haystack:
                results.append((dept_id, p))
    return results[:limit]


# ---------- Форматирование ответа с промптом ----------

def format_prompt_message(dept_id: str, p: dict) -> str:
    return (
        f"<b>{escape_html(p['title'])}</b>\n\n"
        f"💡 <b>Боль:</b> {escape_html(p['pain'])}\n\n"
        f"🎯 <b>Задача:</b> {escape_html(p['task'])}\n\n"
        f"<b>Промпт (скопируйте целиком):</b>\n"
        f"<pre>{escape_html(p['prompt'])}</pre>\n\n"
        f"🔧 <b>Как пользоваться:</b> {escape_html(p['howto'])}"
    )


# ---------- Обработчики ----------

def handle_start(chat_id: int):
    text = (
        "👋 Привет! Это бот-библиотека готовых ИИ-промптов для команды.\n\n"
        "Выберите отдел кнопкой ниже — или просто напишите словами вашу проблему "
        "(например «возражение» или «негатив»), и я найду подходящий промпт."
    )
    send_message(chat_id, text, reply_markup=departments_keyboard())


def handle_text(chat_id: int, text: str):
    if text.strip().startswith("/start"):
        handle_start(chat_id)
        return

    results = search_prompts(text)
    if not results:
        send_message(
            chat_id,
            "Ничего не нашёл по этому слову 🤔 Попробуйте другое ключевое слово "
            "(например часть проблемы: «возврат», «выгорание», «домашка») "
            "или выберите отдел из меню: /start",
        )
        return

    rows = [
        [{"text": f"{DEPARTMENTS[d]['label']} — {p['title']}", "callback_data": f"prompt:{d}:{p['id']}"}]
        for d, p in results
    ]
    send_message(
        chat_id,
        f"Нашёл {len(results)} подходящих промптов:",
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
            text=f"{dept['label']} — выберите промпт:",
            reply_markup=prompts_keyboard(dept_id),
        )
        return

    if data.startswith("prompt:"):
        _, dept_id, prompt_id = data.split(":", 2)
        p = find_prompt(dept_id, prompt_id)
        answer_callback(cq_id)
        if not p:
            send_message(chat_id, "Промпт не найден, попробуйте /start заново.")
            return
        send_message(chat_id, format_prompt_message(dept_id, p), reply_markup=back_keyboard(dept_id))
        return

    answer_callback(cq_id)


# ---------- Главный цикл (long polling) ----------

def run():
    log.info("Бот запущен, жду сообщений...")
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
                log.exception("Ошибка обработки апдейта: %s", e)


if __name__ == "__main__":
    run()
